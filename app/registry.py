from typing import Callable, Dict, Any

class ToolRegistry:
    """
    The ToolRegistry acts as a central phonebook for our functions (tools).
    
    WHY THIS IS NEEDED:
    When we define a Graph in JSON (e.g., via API), we only have strings like "extract_functions".
    We need a way to convert that string back into the actual Python function code to run it.
    This registry holds that mapping: "string_name" -> <function_object>
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        """
        Registers a function so the graph engine can find it later.
        """
        self._tools[name] = func

    def get_tool(self, name: str) -> Callable:
        """
        Retrieves the actual python function using its string name.
        """
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found.")
        return self._tools[name]
    
    def list_tools(self):
        """Returns a list of all available tool names."""
        return list(self._tools.keys())

# Global registry instance
# We use a single global instance so all parts of the app share the same set of tools.
registry = ToolRegistry()
