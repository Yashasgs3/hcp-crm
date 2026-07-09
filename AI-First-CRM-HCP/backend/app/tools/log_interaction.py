from datetime import date, time, datetime

from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.models.interaction import Interaction
from app.llm.parser import extract_interaction


DATE_FIELDS = {"interaction_date", "follow_up_date"}
TIME_FIELDS = {"interaction_time"}

# Date formats to try when normalizing for frontend display (HTML date input needs YYYY-MM-DD)
_DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
]


def _normalize_display_value(value, field: str):
    """Normalize date/time strings to formats compatible with HTML inputs (YYYY-MM-DD / HH:MM)."""
    if value is None or value == "":
        return value
    if not isinstance(value, str):
        return str(value)
    if field in DATE_FIELDS:
        for fmt in _DATE_FORMATS:
            try:
                dt = datetime.strptime(value.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return value
    if field in TIME_FIELDS:
        value = value.strip()
        time_formats = ["%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p", "%I:%M%p"]
        for fmt in time_formats:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%H:%M")
            except ValueError:
                continue
        return value
    return value


def _convert_value(field: str, value):
    """Convert string values to proper Python types for SQLite columns."""
    if value is None or value == "":
        return None
    if field in DATE_FIELDS:
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except (ValueError, TypeError):
                return None
        return value
    if field in TIME_FIELDS:
        if isinstance(value, str):
            try:
                return time.fromisoformat(value)
            except (ValueError, TypeError):
                return None
        return value
    return value


def save_interaction(data: dict):

    db: Session = SessionLocal()

    try:

        interaction = Interaction(

            hcp_name=_convert_value("hcp_name", data.get("hcp_name")),

            specialty=_convert_value("specialty", data.get("specialty")),

            hospital=_convert_value("hospital", data.get("hospital")),

            interaction_type=_convert_value("interaction_type", data.get("interaction_type")),

            interaction_date=_convert_value("interaction_date", data.get("interaction_date")),

            interaction_time=_convert_value("interaction_time", data.get("interaction_time")),

            attendees=_convert_value("attendees", data.get("attendees")),

            discussion_topics=_convert_value("discussion_topics", data.get("discussion_topics")),

            products_discussed=_convert_value("products_discussed", data.get("products_discussed")),

            objections=_convert_value("objections", data.get("objections")),

            materials_shared=_convert_value("materials_shared", data.get("materials_shared")),

            samples_given=_convert_value("samples_given", data.get("samples_given")),

            sentiment=_convert_value("sentiment", data.get("sentiment")),

            summary=_convert_value("summary", data.get("summary")),

            follow_up_required=_convert_value("follow_up_required", data.get("follow_up_required")),

            follow_up_date=_convert_value("follow_up_date", data.get("follow_up_date")),

            next_action=_convert_value("next_action", data.get("next_action")),

            raw_conversation=_convert_value("raw_conversation", data.get("raw_conversation")),
        )

        db.add(interaction)

        db.commit()

        db.refresh(interaction)

        return interaction

    finally:

        db.close()


def log_interaction_node(state):

    conversation = state["user_input"]

    extracted = extract_interaction(conversation)

    # Strip null/empty values so only explicitly stated fields are saved
    extracted = {k: v for k, v in extracted.items() if v is not None and v != ""}
    extracted["raw_conversation"] = conversation

    interaction = save_interaction(extracted)

    # Normalize date/time values for frontend display (HTML date inputs need YYYY-MM-DD)
    display_data = {k: _normalize_display_value(v, k) for k, v in extracted.items()}

    state["interaction_id"] = interaction.id

    state["extracted_data"] = display_data

    state["tool_result"] = {

        "message": "Interaction logged successfully.",

        "interaction_id": interaction.id,

        "interaction": display_data

    }

    return state
