from app.agent.state import AgentState


def router(state: AgentState):
    """
    Decide which tool should be executed.
    """

    intent = state.get("intent")

    if intent == "log":
        return "log_interaction"

    elif intent == "edit":
        return "edit_interaction"

    elif intent == "followup":
        return "followup_tool"

    elif intent == "insights":
        return "hcp_insights"

    elif intent == "materials":
        return "material_recommendation"

    elif intent == "general":
        return "response"

    return "end"
