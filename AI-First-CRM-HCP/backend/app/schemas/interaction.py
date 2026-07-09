from datetime import date, time
from typing import Optional

from pydantic import BaseModel


class InteractionCreate(BaseModel):

    hcp_name: str

    specialty: Optional[str] = None

    hospital: Optional[str] = None

    interaction_type: Optional[str] = None

    interaction_date: Optional[date] = None

    interaction_time: Optional[time] = None

    attendees: Optional[str] = None

    discussion_topics: Optional[str] = None

    products_discussed: Optional[str] = None

    objections: Optional[str] = None

    materials_shared: Optional[str] = None

    samples_given: Optional[str] = None

    sentiment: Optional[str] = None

    summary: Optional[str] = None

    follow_up_required: Optional[str] = None

    follow_up_date: Optional[date] = None

    next_action: Optional[str] = None

    raw_conversation: Optional[str] = None


class InteractionResponse(InteractionCreate):

    id: int

    class Config:
        from_attributes = True
