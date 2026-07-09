from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.config.database import SessionLocal
from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate, InteractionResponse
from app.agent.graph import graph

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/chat", response_model=dict)
async def chat_with_agent(payload: dict = Body(...)):
    """
    Chat endpoint that routes user messages through the LangGraph agent.
    The agent detects intent and executes the appropriate tool.
    """
    user_input = payload.get("message", "")
    interaction_id = payload.get("interaction_id")
    existing_data = payload.get("extracted_data")

    if not user_input.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Build initial state for LangGraph
    initial_state = {
        "user_input": user_input,
        "intent": None,
        "extracted_data": existing_data or {},
        "interaction_id": interaction_id,
        "tool_result": None,
        "response": None,
        "messages": [],
    }

    try:
        result = graph.invoke(initial_state)
        return {
            "success": True,
            "intent": result.get("intent"),
            "tool_result": result.get("tool_result"),
            "response": result.get("response"),
            "interaction_id": result.get("interaction_id"),
            "extracted_data": result.get("extracted_data"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/", response_model=InteractionResponse)
def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db),
):
    """Manually create an interaction record."""
    db_interaction = Interaction(**interaction.model_dump())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


@router.get("/", response_model=list[InteractionResponse])
def list_interactions(
    skip: int = 0,
    limit: int = 20,
    hcp_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all interactions, optionally filtered by HCP name."""
    query = db.query(Interaction)
    if hcp_name:
        query = query.filter(Interaction.hcp_name.ilike(f"%{hcp_name}%"))
    return query.order_by(Interaction.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
):
    """Get a single interaction by ID."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found.")
    return interaction


@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int,
    updates: dict = Body(...),
    db: Session = Depends(get_db),
):
    """Update an interaction record manually."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found.")

    for field, value in updates.items():
        if hasattr(interaction, field) and field != "id":
            setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return interaction


@router.delete("/{interaction_id}")
def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
):
    """Delete an interaction record."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found.")
    db.delete(interaction)
    db.commit()
    return {"message": "Interaction deleted successfully."}


@router.get("/{interaction_id}/history")
def get_interaction_history(
    interaction_id: int,
    db: Session = Depends(get_db),
):
    """Get full history of a specific interaction."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found.")
    return {
        "id": interaction.id,
        "raw_conversation": interaction.raw_conversation,
        "summary": interaction.summary,
        "created_at": str(interaction.created_at),
        "updated_at": str(interaction.updated_at),
    }
