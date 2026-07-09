import json
from datetime import date, time, datetime

from sqlalchemy.orm import Session

from langchain_core.messages import SystemMessage, HumanMessage

from app.config.database import SessionLocal
from app.models.interaction import Interaction
from app.llm.groq_client import get_llm

# Exact column names from the Interaction model
VALID_FIELDS = [
    "hcp_name",
    "specialty",
    "hospital",
    "interaction_type",
    "interaction_date",
    "interaction_time",
    "attendees",
    "discussion_topics",
    "products_discussed",
    "objections",
    "materials_shared",
    "samples_given",
    "sentiment",
    "summary",
    "follow_up_required",
    "follow_up_date",
    "next_action",
]

# Valid options for dropdown fields
DROPDOWN_OPTIONS = {
    "interaction_type": ["In-Person Visit", "Video Call", "Phone Call", "Email", "Conference", "Lunch Meeting"],
    "sentiment": ["Positive", "Neutral", "Negative"],
    "follow_up_required": ["yes", "no"],
}

SYSTEM_PROMPT = f"""
You are an AI CRM Assistant for a Healthcare Professional CRM.

The user is interacting with a form. Your job is to identify what they want to do:

- SET a field to a value
- CLEAR (empty) a field
- DELETE/REMOVE a field value
- RESET multiple fields

VALID FIELD NAMES (use ONLY these exact names):
{chr(10).join(f"- {f}" for f in VALID_FIELDS)}

Return ONLY valid JSON — no markdown, no extra text.

FORMAT:
{{
  "action": "set" | "clear" | "reset" | "options",
  "fields": {{ "field_name": "value" }}  // for "set" — the field values to set
  "clear_fields": ["field_name", ...]    // for "clear" — fields to empty
  "reset_all": true                      // for "reset" — clear everything
  "field": "<field_name>",              // for "options" — the dropdown field name
  "options": ["<list of valid options>"] // for "options" — the valid values
}}

DROPDOWN FIELDS AND THEIR VALID OPTIONS:
{chr(10).join(f"- {k}: {', '.join(v)}" for k, v in DROPDOWN_OPTIONS.items())}

CRITICAL RULE FOR DROPDOWN FIELDS:
If the user mentions interaction_type, sentiment, or follow_up_required but does NOT provide
an exact value that matches one of the valid options above, you MUST return action="options" with
the field name and the list of valid options. The user needs to choose from the list.
ONLY use action="set" for these fields when the value EXACTLY matches one option (case-insensitive).

MAPPINGS (aggressively map user speech to fields):
- "name" / "my name" / "doctor" / "hcp" → hcp_name
- "specialty" / "department" / "field" / "type of doctor" → specialty
- "hospital" / "clinic" / "location" / "place" → hospital
- "date" / "when" / "day" → interaction_date
- "time" / "when" (time context) → interaction_time
- "type" / "visit type" / "interaction" / "interaction type" → interaction_type
- "attendees" / "people" / "who" → attendees
- "topics" / "discussed" / "discussion" → discussion_topics
- "products" / "drugs" → products_discussed
- "objections" / "concerns" → objections
- "materials" / "documents" / "brochures" → materials_shared
- "samples" → samples_given
- "sentiment" / "mood" / "feeling" → sentiment
- "summary" / "notes" / "overview" → summary
- "follow up" / "follow-up" / "next meeting" → follow_up_required/follow_up_date
- "next action" / "next step" / "action item" → next_action

Examples:

User: "My name is Yashas"
Return: {{"action": "set", "fields": {{"hcp_name": "Yashas"}}}}

User: "set hospital to Apollo"
Return: {{"action": "set", "fields": {{"hospital": "Apollo"}}}}

User: "specialty is cardiology"
Return: {{"action": "set", "fields": {{"specialty": "Cardiology"}}}}

User: "interaction type"
Return: {{"action": "options", "field": "interaction_type", "options": ["In-Person Visit", "Video Call", "Phone Call", "Email", "Conference", "Lunch Meeting"]}}

User: "set sentiment"
Return: {{"action": "options", "field": "sentiment", "options": ["Positive", "Neutral", "Negative"]}}

User: "what is the sentiment"
Return: {{"action": "options", "field": "sentiment", "options": ["Positive", "Neutral", "Negative"]}}

User: "interaction type is Video Call"
Return: {{"action": "set", "fields": {{"interaction_type": "Video Call"}}}}

User: "sentiment positive"
Return: {{"action": "set", "fields": {{"sentiment": "Positive"}}}}

User: "follow up required yes"
Return: {{"action": "set", "fields": {{"follow_up_required": "yes"}}}}

User: "clear the name"
Return: {{"action": "clear", "clear_fields": ["hcp_name"]}}

User: "reset the form"
Return: {{"action": "reset", "reset_all": true}}

User: "update name to Dr. Kim and hospital to City General"
Return: {{"action": "set", "fields": {{"hcp_name": "Dr. Kim", "hospital": "City General"}}}}
"""


# Reverse mapping of display labels back to field names
_FIELD_LABEL_MAP = {}
for _f, _kw_list in {
    "hcp_name": ["name", "hcp name", "doctor name", "hcp", "doctor"],
    "specialty": ["specialty", "department", "field"],
    "hospital": ["hospital", "clinic", "location", "place"],
    "interaction_type": ["interaction type", "type", "visit type"],
    "interaction_date": ["interaction date", "date", "day"],
    "interaction_time": ["interaction time", "time"],
    "attendees": ["attendees", "people"],
    "discussion_topics": ["discussion topics", "topics", "discussion"],
    "products_discussed": ["products discussed", "products", "drugs"],
    "objections": ["objections", "concerns"],
    "materials_shared": ["materials shared", "materials", "brochures", "documents"],
    "samples_given": ["samples given", "samples"],
    "sentiment": ["sentiment", "mood", "feeling"],
    "summary": ["summary", "notes", "overview"],
    "follow_up_required": ["follow up required", "follow up", "follow-up required"],
    "follow_up_date": ["follow up date", "follow-up date"],
    "next_action": ["next action", "next step", "action item", "action"],
}.items():
    for _kw in _kw_list:
        _FIELD_LABEL_MAP[_kw] = _f


def _fast_parse_dropdown(user_message: str) -> dict | None:
    """
    Fast-path parsing for pre-formatted dropdown selection messages like
    'interaction type is Video Call' or 'sentiment is Positive'.
    Returns a result dict without calling the LLM, or None if it doesn't match.
    """
    lower = user_message.lower().strip()

    # Check bare field name queries (e.g., "sentiment", "interaction type", "what are the options for sentiment")
    # If the message is just asking about a field, return options for dropdown fields
    for kw, field_name in _FIELD_LABEL_MAP.items():
        if field_name not in DROPDOWN_OPTIONS:
            continue
        if lower == kw:
            return {"action": "options", "field": field_name, "options": DROPDOWN_OPTIONS[field_name]}
        # Check common question patterns with this keyword
        for prefix in ("", "the ", "my ", "what is the ", "what is my ", "what is ",
                       "what are the ", "what are ", "what ", "select ", "choose ",
                       "set ", "pick ", "show me ", "give me ", "list "):
            if lower == prefix + kw or lower.rstrip("?") == prefix + kw:
                return {"action": "options", "field": field_name, "options": DROPDOWN_OPTIONS[field_name]}
        # Also check if the message contains "what ... options ... <field>" patterns
        if ("what" in lower or "show" in lower or "list" in lower) and \
           ("option" in lower or "choice" in lower or "dropdown" in lower) and \
           kw in lower:
            return {"action": "options", "field": field_name, "options": DROPDOWN_OPTIONS[field_name]}

    for kw, field_name in _FIELD_LABEL_MAP.items():
        # Try pattern: "field_label is value"
        pattern = f"{kw} is "
        if lower.startswith(pattern):
            value = user_message[len(pattern):].strip()
            if value:
                # Check if this is a dropdown field with known options
                if field_name in DROPDOWN_OPTIONS:
                    valid_opts = DROPDOWN_OPTIONS[field_name]
                    matched = None
                    for opt in valid_opts:
                        if opt.lower() == value.lower():
                            matched = opt
                            break
                    if matched:
                        return {"action": "set", "fields": {field_name: matched}}
                    # Value doesn't match any option — treat as options request
                    return {"action": "options", "field": field_name, "options": valid_opts}
                else:
                    # Text field — just accept the value as-is
                    return {"action": "set", "fields": {field_name: value}}

        # Try pattern: "field_label value" (without "is")
        # Only for dropdown fields to avoid false matches
        if field_name in DROPDOWN_OPTIONS and lower.startswith(kw + " "):
            value = user_message[len(kw) + 1:].strip()
            if value:
                valid_opts = DROPDOWN_OPTIONS[field_name]
                for opt in valid_opts:
                    if opt.lower() == value.lower():
                        return {"action": "set", "fields": {field_name: opt}}
                return {"action": "options", "field": field_name, "options": valid_opts}

    return None


def extract_updates(user_message: str):
    """Use LLM to extract field updates from the user message."""
    # Fast path: check if this is a pre-formatted dropdown selection
    fast_result = _fast_parse_dropdown(user_message)
    if fast_result is not None:
        return fast_result

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ])

    content = response.content.strip()

    # Strip markdown code fences if present
    if content.startswith("```"):
        lines = content.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    try:
        result = json.loads(content)
        return result
    except Exception:
        return {"action": "set", "fields": {}}


# Fields that need type conversion from string
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
            except ValueError:
                return None
        return value
    if field in TIME_FIELDS:
        if isinstance(value, str):
            try:
                return time.fromisoformat(value)
            except ValueError:
                return None
        return value
    return value


def update_interaction(interaction_id: int, updates: dict):
    """Apply updates to the interaction in the database. Returns (interaction, applied_count)."""
    if not updates or interaction_id is None:
        return None, 0

    db: Session = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(
            Interaction.id == interaction_id
        ).first()

        if interaction is None:
            return None, 0

        applied = 0
        for field, value in updates.items():
            if hasattr(interaction, field):
                converted = _convert_value(field, value)
                setattr(interaction, field, converted)
                applied += 1

        if applied > 0:
            db.commit()
            db.refresh(interaction)

        return interaction, applied
    finally:
        db.close()


def clear_interaction_fields(interaction_id: int, fields: list):
    """Clear specific fields (set to None) in the database."""
    if not fields or interaction_id is None:
        return None, 0

    db: Session = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(
            Interaction.id == interaction_id
        ).first()

        if interaction is None:
            return None, 0

        cleared = 0
        for field in fields:
            if hasattr(interaction, field):
                setattr(interaction, field, None)
                cleared += 1

        if cleared > 0:
            db.commit()
            db.refresh(interaction)

        return interaction, cleared
    finally:
        db.close()


def _field_label(field: str) -> str:
    """Human-readable label for a field name."""
    return field.replace("_", " ")


def edit_interaction_node(state):
    """LangGraph node: handle edit intent."""
    interaction_id = state.get("interaction_id")
    user_message = state["user_input"]
    existing_data = state.get("extracted_data") or {}

    result = extract_updates(user_message)
    action = result.get("action", "set")

    # --- OPTIONS: user asked about a dropdown field without providing a valid value ---
    if action == "options":
        field = result.get("field", "")
        options = result.get("options", [])
        if field and options:
            opts_str = ", ".join(options)
            state["tool_result"] = {
                "message": f"Please choose {_field_label(field)}:",
                "updated_fields": {},
                "options": {
                    "field": field,
                    "values": options,
                },
            }
        else:
            state["tool_result"] = {
                "message": "Please choose from the available options for that field.",
                "updated_fields": {},
            }
        return state

    # --- RESET: clear all form data ---
    if action == "reset":
        cleared = {}
        for f in VALID_FIELDS:
            cleared[f] = ""

        if interaction_id:
            clear_interaction_fields(interaction_id, VALID_FIELDS)

        state["tool_result"] = {
            "message": "Form has been reset. All fields cleared.",
            "updated_fields": {},
            "interaction": {},
        }
        state["extracted_data"] = {}
        return state

    # --- CLEAR: remove specific fields ---
    if action == "clear":
        clear_list = result.get("clear_fields", [])
        valid_clears = [f for f in clear_list if f in VALID_FIELDS]

        if not valid_clears:
            lower = user_message.lower()
            inferred = []
            field_keywords = {
                "hcp_name": ["name", "doctor", "hcp"],
                "specialty": ["specialty", "department"],
                "hospital": ["hospital", "clinic", "location"],
                "interaction_date": ["date", "day"],
                "interaction_time": ["time"],
                "interaction_type": ["type", "visit"],
                "attendees": ["attendees", "people"],
                "discussion_topics": ["topics", "discussion"],
                "products_discussed": ["products", "drugs"],
                "objections": ["objections", "concerns"],
                "materials_shared": ["materials", "brochures"],
                "samples_given": ["samples"],
                "sentiment": ["sentiment", "mood"],
                "summary": ["summary", "notes"],
                "follow_up_required": ["follow up", "follow-up"],
                "follow_up_date": ["follow up date"],
                "next_action": ["next action", "next step", "action"],
            }
            for f_name, keywords in field_keywords.items():
                for kw in keywords:
                    if kw in lower:
                        inferred.append(f_name)
                        break
            valid_clears = inferred

        if not valid_clears:
            state["tool_result"] = {
                "message": "I couldn't identify which field to clear. Try 'clear the name' or 'delete the hospital'.",
                "updated_fields": {},
            }
            return state

        cleared_data = {}
        for f in valid_clears:
            cleared_data[f] = ""

        if interaction_id:
            clear_interaction_fields(interaction_id, valid_clears)

        field_names = [_field_label(f) for f in valid_clears]
        if len(field_names) == 1:
            msg = f"Cleared {field_names[0]}."
        else:
            msg = f"Cleared {', '.join(field_names[:-1])} and {field_names[-1]}."

        merged = {**existing_data, **cleared_data}
        state["tool_result"] = {
            "message": msg,
            "updated_fields": cleared_data,
            "interaction": merged,
        }
        state["extracted_data"] = merged
        return state

    # --- SET: update fields with values ---
    fields = result.get("fields", {})
    valid_fields = {k: v for k, v in fields.items() if k in VALID_FIELDS}

    # If no fields from LLM, try direct keyword extraction
    if not valid_fields:
        lower = user_message.lower()
        field_patterns = {
            "hcp_name": ["name is", "my name is", "the name is", "doctor is", "hcp is"],
            "specialty": ["specialty is", "department is", "field is"],
            "hospital": ["hospital is", "clinic is", "location is", "place is"],
            "interaction_date": ["date is", "the date is"],
            "interaction_time": ["time is", "the time is"],
            "interaction_type": ["type is", "interaction type is"],
            "sentiment": ["sentiment is", "mood is"],
            "follow_up_required": ["follow up is", "follow-up is"],
        }
        for f_name, patterns in field_patterns.items():
            for pat in patterns:
                if pat in lower:
                    idx = lower.find(pat) + len(pat)
                    value = lower[idx:].strip().rstrip(".")
                    if value:
                        valid_fields[f_name] = value
                    break

    if not valid_fields:
        state["tool_result"] = {
            "message": (
                "I couldn't identify which form field to update. "
                "Try something like 'name is Dr. Smith', 'hospital is Apollo', "
                "'specialty is cardiology', or 'clear the date'."
            ),
            "updated_fields": {},
        }
        return state

    # If there's an existing interaction in the DB, apply updates to it
    if interaction_id:
        interaction, applied = update_interaction(interaction_id, valid_fields)

        if interaction is not None and applied > 0:
            changed_names = [_field_label(k) for k in valid_fields.keys()]
            if len(changed_names) == 1:
                val = list(valid_fields.values())[0]
                msg = f"Updated {changed_names[0]} to: {val}"
            elif len(changed_names) == 2:
                msg = f"Updated {changed_names[0]} and {changed_names[1]}."
            else:
                msg = f"Updated {', '.join(changed_names[:-1])} and {changed_names[-1]}."

            updated_data = {}
            for f_name in VALID_FIELDS:
                val = getattr(interaction, f_name, None)
                if val is not None:
                    str_val = str(val) if not isinstance(val, str) else val
                    updated_data[f_name] = _normalize_display_value(str_val, f_name)

            normalized_fields = {k: _normalize_display_value(v, k) for k, v in valid_fields.items()}

            state["tool_result"] = {
                "message": msg,
                "updated_fields": normalized_fields,
                "interaction_id": interaction.id,
                "interaction": updated_data,
            }
            state["extracted_data"] = updated_data
            return state

    # Normalize all fields for HTML display (dates → YYYY-MM-DD, times → HH:MM)
    normalized_fields = {k: _normalize_display_value(v, k) for k, v in valid_fields.items()}

    # No DB interaction — just populate the form
    merged = {**existing_data, **normalized_fields}

    field_entries = list(normalized_fields.items())
    if len(field_entries) == 1:
        msg = f"Set {_field_label(field_entries[0][0])} to: {field_entries[0][1]}"
    else:
        names = [_field_label(k) for k in normalized_fields.keys()]
        msg = f"Set {', '.join(names[:-1])} and {names[-1]}."

    state["tool_result"] = {
        "message": msg,
        "updated_fields": normalized_fields,
        "interaction": merged,
    }
    state["extracted_data"] = merged

    return state
