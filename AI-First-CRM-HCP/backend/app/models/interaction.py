from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime
from sqlalchemy.sql import func

from app.config.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)

    # HCP Details
    hcp_name = Column(String(255), nullable=True)
    specialty = Column(String(255))
    hospital = Column(String(255))

    # Interaction Details
    interaction_type = Column(String(100))
    interaction_date = Column(Date)
    interaction_time = Column(Time)

    attendees = Column(Text)

    # Discussion
    discussion_topics = Column(Text)
    products_discussed = Column(Text)
    objections = Column(Text)

    # Materials
    materials_shared = Column(Text)
    samples_given = Column(Text)

    # AI Generated
    sentiment = Column(String(100))
    summary = Column(Text)

    # Follow-up
    follow_up_required = Column(String(20))
    follow_up_date = Column(Date)
    next_action = Column(Text)

    # Chat History
    raw_conversation = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
