# Tredence_Assignment

# Agent Workflow Engine

A simple yet powerful backend workflow engine for defining and executing agentic workflows. Built with Python and FastAPI.

## Project Structure
- `app/engine.py`: Core graph execution logic (Nodes, Edges, State).
- `app/registry.py`: Tool registry for managing functions.
- `app/workflows/`: Example workflows (e.g., Code Review Agent).
- `app/main.py`: FastAPI application serving the API.

## Features
- **Graph-based Execution**: Define workflows as nodes and edges.
- **State Management**: Shared state passed between nodes.
- **Branching & Looping**: Conditional edges allow for complex logic.
- **REST API**: Create and run workflows via HTTP.

## How to Run
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Run the verification script (optional):
   ```bash
   python test_workflow_script.py
   ```

## API Usage

### Run Example Workflow (Code Review)
**POST** `/graph/run`
```json
{
  "graph_id": "code-review-agent",
  "initial_state": {
    "code": "def test():\n  print('bad')"
  }
}
```

### Create New Graph
**POST** `/graph/create`
```json
{
  "name": "MyGraph",
  "nodes": [{"name": "A", "tool_name": "tool_a"}],
  "edges": [{"source_node": "A", "target_node": "B"}]
}
```

## Future Improvements
- **Persistence**: Store graphs/runs in a DB (SQLite/Postgres).
- **Async Nodes**: Fully async Celery/Background task support for long-running nodes.
- **Dynamic Tools**: stronger serialization for tool inputs/outputs.

## Testing

### 1. Python API Test Script
I have included a script `test_api_usage.py` that hits the running API.
```bash
pip install requests
python test_api_usage.py
```

### 2. Swagger UI
Open your browser to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to see the interactive API documentation. You can try out endpoints directly from the browser.

### 3. Curl Example
```bash
curl -X POST "http://127.0.0.1:8000/graph/run" \
-H "Content-Type: application/json" \
-d '{"graph_id": "code-review-agent", "initial_state": {"code": "def test():\n print(1)"}}'
-d '{
  "graph_id": "code-review-agent",
  "initial_state": {
    "code": "def test():\n    print('bad')",
    "quality_score": 0,
    "issues": []
  }
}'

```
