import asyncio
from app.registry import registry
from app.engine import Graph, Node, Edge
from app.workflows.code_review import create_code_review_graph

async def test_code_review_workflow():
    """
    Verifies that the Code Review Agent works correctly without needing the API server.
    """
    print("Setting up Code Review Workflow...")
    graph = create_code_review_graph()
    
    # Broken code example
    initial_state = {
        "code": "def hello():\n    print('hello world')\n\ndef add(a, b):\n    return a + b",
        "log": []
    }
    
    print("\nRunning workflow with 'broken' code...")
    # Core execution call
    result = await graph.run(initial_state, registry)
    
    final_state = result["final_state"]
    logs = result["logs"]
    
    print(f"\nWorkflow finished in {len(logs)} steps.")
    print("\nFinal Code Snapshot:")
    print(final_state["code"])
    print(f"\nFinal Quality Score: {final_state.get('quality_score')}")
    print(f"Issue Count: {final_state.get('issue_count')}")
    
    # Assertions
    assert final_state["issue_count"] == 0, "Issues should be resolved"
    assert "# print" in final_state["code"], "Fix should be applied (print commented out)"
    print("\nTest Passed! Logic is working.")

if __name__ == "__main__":
    asyncio.run(test_code_review_workflow())
