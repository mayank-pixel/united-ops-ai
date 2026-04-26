from typing import Annotated, TypedDict, List, Union
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The shared memory state for our LangGraph workflow.
    """
    # LangGraph will automatically append new messages to this list
    messages: Annotated[List, add_messages]
    
    aircraft_model: str
    fault_code: str
    
    # These will be filled by our CrewAI agents
    technical_steps: str
    safety_warnings: str
    is_safety_cleared: bool