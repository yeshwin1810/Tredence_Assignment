import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    """Test the root endpoint to ensure server is up."""
    print("Checking server status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("âœ… Server is running!")
            print(f"   Response: {response.json()}")
        else:
            print(f"âŒ Server returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("âŒ Could not connect to server. Is it running?")
        return False
    return True

def test_run_workflow():
    """
    Test running the pre-loaded code-review workflow via the API.
    WHY: Ensures the API correctly calls the engine and returns results.
    """
    print("\nTesting '/graph/run' with Code Review Agent...")
    
    payload = {
        "graph_id": "code-review-agent",
        "initial_state": {
            "code": "def divide(a, b):\n    print(a/b)\n    return a/b",
            "log": []
        }
    }
    
    response = requests.post(f"{BASE_URL}/graph/run", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("âœ… Workflow executed successfully!")
        print(f"   Run ID: {data['run_id']}")
        
        final_code = data["final_state"].get("code")
        print("\n--- Final Code ---")
        print(final_code)
        print("------------------")
        
        if "# print" in final_code:
            print("âœ… Verified: 'print' statement was commented out.")
        else:
            print("âŒ Failed: 'print' statement was NOT commented out.")
    else:
        print(f"âŒ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Ensure requests is installed: pip install requests
    if test_root():
        test_run_workflow()
