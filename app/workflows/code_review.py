from app.registry import registry
from app.engine import Graph, Node, Edge

# --- Tool Definitions ---

def extract_functions(state):
    """
    Step 1: Parse the code.
    WHY: We need to understand the structure before we can check it.
    """
    code = state.get("code", "")
    # Mock extraction: just split by "def "
    functions = [f.split("(")[0] for f in code.split("def ")[1:]]
    return {"functions": functions, "log": state.get("log", []) + [f"Extracted {len(functions)} functions"]}

def check_complexity(state):
    """
    Step 2: Check standard metrics.
    WHY: High complexity usually means bad code.
    """
    code = state.get("code", "")
    # Mock complexity: length of code / 10
    complexity = len(code) / 10
    return {"complexity": complexity, "log": state.get("log", []) + [f"Calculated complexity: {complexity}"]}

def detect_issues(state):
    """
    Step 3: Detect "Bugs".
    WHY: This is the core 'reasoning' step. We look for patterns we don't like.
    """
    code = state.get("code", "")
    issues = []
    
    # Rule 1: Flask usage check
    if "request" not in code and "flask" in code:
        issues.append("Using Flask but not request")
    
    # Rule 2: No print statements in production code
    lines = code.split("\n")
    for line in lines:
        if "print(" in line and not line.strip().startswith("#"):
             issues.append(f"Avoid using print statement: {line.strip()}")
             break # limit to one report per pass to simplify logic
    
    return {"issues": issues, "issue_count": len(issues), "log": state.get("log", []) + [f"Detected {len(issues)} issues"]}

def suggest_improvements(state):
    """
    Step 4: Fix the code.
    WHY: Agents shouldn't just complain, they should help. 
    This step modifies the code state to resolve the issues found in Step 3.
    """
    code = state.get("code", "")
    issues = state.get("issues", [])
    
    # Mock improvement: actually fix the issue to stop the loop
    new_code = code
    for issue in issues:
        if "print" in issue:
            new_code = new_code.replace("print(", "# print(") # Comment out the offender
        else:
             new_code += f"\n# FIX: {issue}"
    
    # Increase quality score
    quality_score = state.get("quality_score", 0) + 20
    
    return {
        "code": new_code, 
        "quality_score": quality_score, 
        "issues": [], # assume fixed
        "issue_count": 0,
        "log": state.get("log", []) + ["Applied improvements"]
    }

# Register Tools
registry.register("extract_functions", extract_functions)
registry.register("check_complexity", check_complexity)
registry.register("detect_issues", detect_issues)
registry.register("suggest_improvements", suggest_improvements)

# --- Graph Definition ---

def create_code_review_graph():
    """
    Builds the Graph structure.
    State flows: Extract -> Check -> Detect -> [Decision]
    Decision:
      - If issues found -> Suggest (Fix) -> Check (Loop back)
      - If no issues -> End
    """
    graph = Graph(name="CodeReviewAgent", start_node="extract")

    # Nodes
    graph.add_node(Node(name="extract", tool_name="extract_functions"))
    graph.add_node(Node(name="check", tool_name="check_complexity"))
    graph.add_node(Node(name="detect", tool_name="detect_issues"))
    graph.add_node(Node(name="suggest", tool_name="suggest_improvements"))

    # Edges
    graph.add_edge(Edge(source_node="extract", target_node="check"))
    graph.add_edge(Edge(source_node="check", target_node="detect"))
    
    # Branching Condition
    def has_issues(state):
        return state.get("issue_count", 0) > 0
    
    # Logic: detect -> (if issues) -> suggest -> check
    #        detect -> (no issues) -> END
    
    graph.add_edge(Edge(source_node="detect", target_node="suggest", condition=has_issues))
    # If no issues, we stop. My engine logic: "If no edge found, we are at a terminal node".
    # So if has_issues is false, it returns None, so loop ends.
    
    # Loop back from suggest to check (to re-eval complexity and ensure no new regressions during fix)
    graph.add_edge(Edge(source_node="suggest", target_node="check"))

    return graph
