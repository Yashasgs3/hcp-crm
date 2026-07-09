from app.agent.state import AgentState

from app.agent.planner import detect_intent

from app.llm.groq_client import get_llm
from langchain_core.messages import SystemMessage, HumanMessage


def planner_node(state: AgentState):

    state["intent"] = detect_intent(state["user_input"])

    return state


GENERAL_RESPONSE_PROMPT = """You are an AI assistant for a Healthcare Professional (HCP) CRM system.
You help pharmaceutical sales representatives log and manage interactions with doctors and healthcare professionals.

Be friendly, concise, and helpful. The user just sent you a message that wasn't a specific command.
Respond naturally to their message. If they're greeting you, greet them back.
If they're asking what you can do, describe your capabilities briefly.

Capabilities:
- Log HCP interactions (describe a meeting and I'll extract details)
- Edit interaction details (tell me what to fix)
- Suggest follow-up actions
- Provide HCP insights
- Recommend materials for your next visit"""


def response_node(state: AgentState):

    result = state.get("tool_result")
    intent = state.get("intent", "")

    if result:
        state["response"] = result.get(
            "message",
            "Task completed successfully."
        )
    elif intent == "general":
        user_input = state.get("user_input", "")
        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content=GENERAL_RESPONSE_PROMPT),
            HumanMessage(content=user_input)
        ])
        state["response"] = response.content.strip()
    else:
        state["response"] = "Done."

    return state
