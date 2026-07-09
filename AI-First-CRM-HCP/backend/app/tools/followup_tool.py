import json
from sqlalchemy.orm import Session
from langchain_core.messages import SystemMessage, HumanMessage

from app.config.database import SessionLocal
from app.models.interaction import Interaction
from app.llm.groq_client import get_llm

SYSTEM_PROMPT = """
You are an AI CRM Assistant for pharmaceutical sales representatives.

Your job is to analyze the current interaction and suggest the best follow-up actions.

Return ONLY JSON with these fields:
- suggested_date: A recommended date for follow-up (YYYY-MM-DD format, pick a date 1-4 weeks from the interaction_date provided)
- suggested_action: A specific next action (e.g., "Send clinical trial data", "Schedule lunch meeting", "Drop off samples")
- priority: One of "high", "medium", or "low" based on the interaction sentiment and HCP engagement
- reasoning: Brief 1-2 sentence explanation of why this follow-up is recommended

Rules:
1. Base your suggestion on the discussion topics, sentiment, and products discussed.
2. If the interaction was negative/short, suggest a gentle re-engagement approach.
3. If samples were requested, prioritize sample delivery.
4. Never invent HCP names or details not in the context.
"""

def generate_followup(interaction_data: dict) -> dict:
    """Generate follow-up recommendations for a logged interaction."""
    llm = get_llm()
    context = json.dumps(interaction_data, default=str)

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Interaction data:\n{context}")
    ])

    try:
        return json.loads(response.content)
    except Exception:
        return {
            "suggested_date": None,
            "suggested_action": "Review interaction and plan follow-up",
            "priority": "medium",
            "reasoning": "Unable to generate specific recommendation."
        }


def save_followup(interaction_id: int, followup_data: dict) -> dict:
    """Save follow-up recommendation to the interaction record."""
    db: Session = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(
            Interaction.id == interaction_id
        ).first()

        if interaction:
            if followup_data.get("suggested_date"):
                interaction.follow_up_date = followup_data["suggested_date"]
            interaction.next_action = followup_data.get("suggested_action", interaction.next_action)
            interaction.follow_up_required = "yes"
            db.commit()

        return followup_data
    finally:
        db.close()


def followup_node(state):
    """LangGraph node: generate follow-up recommendations."""
    interaction_id = state.get("interaction_id")
    extracted_data = state.get("extracted_data", {})

    if not interaction_id:
        state["tool_result"] = {
            "message": "Please log an interaction first before requesting follow-up suggestions."
        }
        return state

    followup_data = generate_followup(extracted_data)
    save_followup(interaction_id, followup_data)

    state["tool_result"] = {
        "message": "Follow-up recommendation generated.",
        "followup": followup_data,
        "interaction_id": interaction_id,
    }
    return state
