from typing import TypedDict, Optional, Dict, List


class AgentState(TypedDict):
    """
    Shared state passed between LangGraph nodes.
    """

    # User chat message
    user_input: str

    # Intent detected by planner
    intent: Optional[str]

    # Extracted interaction data
    extracted_data: Optional[Dict]

    # Current interaction ID
    interaction_id: Optional[int]

    # Tool output
    tool_result: Optional[Dict]

    # AI Response
    response: Optional[str]

    # Conversation history
    messages: List[str]
