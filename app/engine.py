import asyncio
from typing import Dict, List, Any, Optional, Callable, NotRequired, TypedDict
from pydantic import BaseModel, Field

# WHY: We use a flexible Dictionary for State so that any node can add any data it wants.
# Ideally this would be a Pydantic model for stricter validation, but a dict is easier for a generic engine.
State = Dict[str, Any]

class Edge(BaseModel):
    """
    Represents a connection between two nodes. 
    It tells the engine: "After checking 'source_node', where do I go next?"
    """
    source_node: str
    target_node: str
    # WHY: Conditions allow for "Branching". e.g., "Only go to 'Refine' IF 'score < 5'"
    condition: Optional[Callable[[State], bool]] = None
    condition_name: Optional[str] = None # For serialization/API purposes

class Node(BaseModel):
    """
    A single step in our workflow. 
    It points to a tool (function) name in the registry that does the actual work.
    """
    name: str
    tool_name: str # Name of the function in the registry

class Graph:
    """
    The orchestrator. It manages the flow of execution from one node to another.
    """
    def __init__(self, name: str, start_node: str):
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.start_node = start_node

    def add_node(self, node: Node):
        self.nodes[node.name] = node

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    async def run(self, initial_state: State, tool_registry) -> Dict[str, Any]:
        """
        The main loop that executes the workflow.
        
        HOW IT WORKS:
        1. Start at the 'start_node'.
        2. Execute the tool associated with that node.
        3. Update the shared 'state' with the results.
        4. "Router Step": Check all Edges to see which node to visit next.
           - If a conditional edge evaluates to True, take it.
           - Otherwise take the unconditional edge.
        5. Repeat until no edges match (End of graph).
        """
        current_node_name = self.start_node
        state = initial_state.copy()
        logs = []
        steps = 0
        MAX_STEPS = 100 # WHY: Safety brake to prevent infinite loops from freezing the server.

        while current_node_name and steps < MAX_STEPS:
            if current_node_name not in self.nodes:
                raise ValueError(f"Node '{current_node_name}' not found in graph.")

            node = self.nodes[current_node_name]
            
            # Execute Node
            try:
                # WHY: We look up the function code using the string name from the registry
                tool_func = tool_registry.get_tool(node.tool_name)
                
                # We assume tools take 'state' as argument and return a dict of updates
                updates = await self._execute_tool(tool_func, state)
                
                # Update state
                if isinstance(updates, dict):
                    state.update(updates)
                
                logs.append({
                    "step": steps,
                    "node": current_node_name,
                    "updates": updates,
                    "state_snapshot": state.copy() # Snapshot for debugging
                })
            except Exception as e:
                logs.append({
                    "step": steps,
                    "node": current_node_name,
                    "error": str(e)
                })
                raise e

            steps += 1
            
            # Determine next node
            current_node_name = self._get_next_node(current_node_name, state)

        return {"final_state": state, "logs": logs}

    async def _execute_tool(self, func: Callable, state: State) -> Any:
        """Helper to run both sync and async functions seamlessly."""
        if asyncio.iscoroutinefunction(func):
            return await func(state)
        else:
            return func(state)

    def _get_next_node(self, current_node: str, state: State) -> Optional[str]:
        """
        Logic to decide where to go next.
        It evaluates conditions on edges starting from the current node.
        """
        # Find all edges starting from current_node
        possible_edges = [e for e in self.edges if e.source_node == current_node]
        
        for edge in possible_edges:
            if edge.condition:
                # WHY: Dynamic routing based on the data in 'state'
                if edge.condition(state):
                    return edge.target_node
            else:
                # Unconditional edge (Default path)
                return edge.target_node
        
        # If no edge found, we are at a terminal node (End of logic)
        return None
