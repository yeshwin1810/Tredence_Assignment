from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from app.engine import Graph, Node, Edge, State
from app.registry import registry
from app.workflows.code_review import create_code_review_graph

app = FastAPI(title="Agent Workflow Engine")

# In-memory storage
# WHY: For this assignment, we use RAM. In production, this would be a Postgres/Redis database.
graphs: Dict[str, Graph] = {}
runs: Dict[str, Dict[str, Any]] = {}

# Pre-load the example workflow
example_graph = create_code_review_graph()
graphs["code-review-agent"] = example_graph

# --- Models ---

class NodeModel(BaseModel):
    name: str # The ID of the node in the graph
    tool_name: str # The function it calls

class EdgeModel(BaseModel):
    source_node: str
    target_node: str
    condition_name: Optional[str] = None

class CreateGraphRequest(BaseModel):
    name: str
    nodes: List[NodeModel]
    edges: List[EdgeModel]

class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

# --- API Endpoints ---

@app.post("/graph/create")
def create_graph(request: CreateGraphRequest):
    """
    Registers a new graph definition dynamically via API.
    """
    graph_id = str(uuid.uuid4())
    graph = Graph(name=request.name, start_node=request.nodes[0].name if request.nodes else "")
    
    for n in request.nodes:
        graph.add_node(Node(name=n.name, tool_name=n.tool_name))
    
    for e in request.edges:
        # Note: Dynamic condition loading is unsafe/complex for a simple demo.
        # We will support basic named conditions if needed, otherwise conditional edges 
        # via API might be limited to "Pre-defined" conditions in this simple version.
        # For now, we'll just add unconditional edges for API created graphs.
        graph.add_edge(Edge(source_node=e.source_node, target_node=e.target_node))
        
    graphs[graph_id] = graph
    return {"graph_id": graph_id, "message": "Graph created successfully"}

@app.post("/graph/run")
async def run_graph(request: RunGraphRequest, background_tasks: BackgroundTasks):
    """
    Executes a workflow.
    Blocks until completion (for simplicity) and returns the final state.
    """
    if request.graph_id not in graphs:
        # Check if it's the named example
        if request.graph_id == "code-review-agent":
            pass # exists
        else:
             raise HTTPException(status_code=404, detail="Graph not found")
    
    run_id = str(uuid.uuid4())
    graph = graphs[request.graph_id]
    
    # Initialize run status
    runs[run_id] = {"status": "running", "state": request.initial_state, "logs": []}

    try:
        # Run the engine
        result = await graph.run(request.initial_state, registry)
        
        runs[run_id]["status"] = "completed"
        runs[run_id]["state"] = result["final_state"]
        runs[run_id]["logs"] = result["logs"]
        return {"run_id": run_id, "final_state": result["final_state"], "logs": result["logs"]}
    except Exception as e:
        runs[run_id]["status"] = "failed"
        runs[run_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/state/{run_id}")
def get_run_state(run_id: str):
    """
    Retrieves the status and result of a specific run.
    """
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return runs[run_id]

@app.get("/tools")
def list_tools():
    return {"tools": registry.list_tools()}

@app.get("/")
def read_root():
    return {"message": "Agent Workflow Engine is running. Use /docs for API."}
