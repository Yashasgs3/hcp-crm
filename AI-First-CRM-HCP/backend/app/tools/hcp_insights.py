import json
from typing import List
from sqlalchemy.orm import Session
from langchain_core.messages import SystemMessage, HumanMessage

from app.config.database import SessionLocal
from app.models.interaction import Interaction
from app.llm.groq_client import get_llm

SYSTEM_PROMPT = """
You are an AI CRM Insights Analyst for pharmaceutical sales representatives.

Your job is to analyze past interactions with an HCP and generate actionable insights.

Return ONLY JSON with these fields:
- total_interactions: Number of past interactions found
- last_interaction_date: Most recent interaction date
- sentiment_trend: One of "improving", "stable", "declining", or "unknown"
- preferred_topics: List of topics the HCP engages with most (max 3)
- recommended_approach: Brief strategic recommendation for the next visit
- key_relationship_notes: 1-2 sentence summary of the relationship status

Rules:
1. Only use data from the provided interaction history.
2. If no history exists, set total_interactions to 0 and note that in key_relationship_notes.
3. Be concise and actionable.
4. Never fabricate data.
"""

def get_hcp_interactions(hcp_name: str) -> List[dict]:
    """Fetch all past interactions for a given HCP."""
    db: Session = SessionLocal()
    try:
        interactions = db.query(Interaction).filter(
            Interaction.hcp_name.ilike(f"%{hcp_name}%")
        ).order_by(Interaction.created_at.desc()).all()

        return [
            {
                "id": i.id,
                "hcp_name": i.hcp_name,
                "specialty": i.specialty,
                "hospital": i.hospital,
                "interaction_date": str(i.interaction_date) if i.interaction_date else None,
                "discussion_topics": i.discussion_topics,
                "products_discussed": i.products_discussed,
                "sentiment": i.sentiment,
                "summary": i.summary,
                "next_action": i.next_action,
            }
            for i in interactions
        ]
    finally:
        db.close()


def generate_insights(interactions: List[dict], hcp_name: str) -> dict:
    """Generate AI-powered insights from HCP interaction history."""
    if not interactions:
        return {
            "total_interactions": 0,
            "last_interaction_date": None,
            "sentiment_trend": "unknown",
            "preferred_topics": [],
            "recommended_approach": f"No prior interactions found for {hcp_name}. Start with an introductory visit.",
            "key_relationship_notes": f"This appears to be a new HCP with no recorded interaction history.",
        }

    llm = get_llm()
    context = json.dumps(interactions, default=str)

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"HCP Name: {hcp_name}\n\nPast Interactions:\n{context}")
    ])

    try:
        return json.loads(response.content)
    except Exception:
        return {
            "total_interactions": len(interactions),
            "last_interaction_date": interactions[0].get("interaction_date") if interactions else None,
            "sentiment_trend": "unknown",
            "preferred_topics": [],
            "recommended_approach": "Review past interactions manually.",
            "key_relationship_notes": "Unable to generate automated insights.",
        }


def insights_node(state):
    """LangGraph node: analyze HCP interaction history and provide insights."""
    user_input = state.get("user_input", "")
    extracted_data = state.get("extracted_data", {})

    hcp_name = extracted_data.get("hcp_name") or user_input

    interactions = get_hcp_interactions(hcp_name)
    insights = generate_insights(interactions, hcp_name)

    state["tool_result"] = {
        "message": f"Insights generated for {hcp_name}.",
        "insights": insights,
        "hcp_name": hcp_name,
        "total_interactions": len(interactions),
    }
    return state
