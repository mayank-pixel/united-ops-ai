from langgraph.graph import StateGraph, START, END
from src.graph.state import AgentState
from src.graph.nodes import research_and_audit_node

def create_maintenance_workflow():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("maintenance_specialists", research_and_audit_node)

    # Define edges
    workflow.add_edge(START, "maintenance_specialists")
    workflow.add_edge("maintenance_specialists", END)

    return workflow.compile()

# This part allows the 'uv run python' command to actually print something
if __name__ == "__main__":
    app = create_maintenance_workflow()
    print("✅ Workflow Compiled Successfully!")