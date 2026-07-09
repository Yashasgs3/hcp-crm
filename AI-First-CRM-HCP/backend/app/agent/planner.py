from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.groq_client import get_llm


SYSTEM_PROMPT = """
You are an AI planner for a Healthcare Professional (HCP) CRM.

Identify the user's intent.

Return ONLY ONE WORD — no punctuation, no extra text.

Possible intents:

log       - user is describing a new HCP interaction, meeting, or doctor visit to record
edit      - user wants to update/change/add/clear/remove/fill/set any form field value
followup  - user wants follow-up suggestions for a past interaction
insights  - user wants HCP insights, stats, or interaction history
materials - user wants material or document recommendations
general   - general chat, greeting, small-talk, or anything unrelated to the CRM

CRITICAL RULE: If the user mentions ANY form field (name, date, hospital, specialty, etc.)
or says anything about the form, it is ALWAYS `edit`. Even single-word answers that look
like field values should be treated as `edit`.

Examples:

Today I met Dr Smith at Mercy Hospital -> log

Actually, it was Dr John, not Dr Smith -> edit
The hospital was Apollo Hospital -> edit
Change the date to May 7th -> edit
Add my name to the form -> edit
Fill the name field with Dr. Brown -> edit
Name is Dr. Yashas -> edit
My name is Yashas -> edit
Name is Yashas -> edit
specialty is cardiology -> edit
hospital is Apollo -> edit
date is May 7 -> edit
clear the name -> edit
remove the hospital -> edit
delete the date -> edit
reset the form -> edit
the name should be John -> edit
put cardiology in specialty -> edit
make the hospital City General -> edit

Suggest a follow-up for Dr Chen -> followup
Show me insights for Dr. Sarah Chen -> insights
What materials should I bring next time? -> materials

Hi -> general
Thanks -> general
"""


# Comprehensive keyword patterns for edit intent — checked before LLM call
EDIT_KEYWORDS = [
    # Form-filling phrases
    "fill the", "fill out", "fill in", "fill my", "fill this",
    "put my", "put the", "put ", "add to the form", "add this to",
    "update the", "update my", "change the", "change my",
    "set the", "set my", "set ",
    "make the", "make my",
    "please fill", "please add", "please set", "please update",
    "write ", "enter ",

    # Name patterns
    "my name is", "my name", "name is", "name should be", "name as",
    "the name is", "the name",
    "doctor name", "dr name", "hcp name",

    # Field-value declarative patterns
    "hospital is", "hospital should be", "the hospital",
    "specialty is", "specialty should be", "the specialty",
    "date is", "the date is", "the date",
    "time is", "the time",
    "attendees are", "attendees is",
    "sentiment is", "the sentiment",
    "summary is", "the summary",

    # Clear/delete/reset patterns
    "clear the", "clear my",
    "remove the", "remove my",
    "delete the", "delete my",
    "reset the", "reset my",
    "erase the", "erase my",
    "wipe the",

    # More patterns
    "my date of birth", "my birthday",
    "insert ", "save ",
    "in the form", "on the form", "to the form",
]

LOG_PATTERNS = [
    "i met", "i just met", "i saw", "i visited", "i had a",
    "today i", "just had", "spoke with", "talked to",
]


def _precheck_intent(text: str) -> str | None:
    """Quick keyword-based intent check. Returns intent string or None if LLM is needed."""
    lower = text.lower().strip()

    # Strong edit signals — check first since these are most common
    for kw in EDIT_KEYWORDS:
        if kw in lower:
            return "edit"

    # Strong log signals (describing a meeting/visit)
    for pat in LOG_PATTERNS:
        if lower.startswith(pat):
            return "log"

    # Dropdown / option field queries (user asking about interaction type, sentiment, etc.)
    dropdown_queries = [
        "interaction type", "what type", "type of interaction",
        "sentiment", "what sentiment", "how did it go",
        "follow up required", "follow-up required",
        "select type", "choose type", "pick type",
        "select sentiment", "choose sentiment", "pick sentiment",
        "what is the type", "what is the sentiment",
        "set type", "set sentiment", "set interaction",
    ]
    for dq in dropdown_queries:
        if dq in lower:
            return "edit"

    # Heuristic: if the message is very short (1-4 words) and isn't a greeting,
    # it's likely a field value being set
    word_count = len(lower.split())
    greetings = {"hi", "hey", "hello", "thanks", "thank you", "ok", "okay", "yes", "no", "what", "help"}
    if word_count <= 4 and lower not in greetings:
        # Short message — probably setting a field value
        return "edit"

    return None  # LLM decides


def detect_intent(text: str):
    # Try keyword pre-check first to avoid LLM misclassification
    pre = _precheck_intent(text)
    if pre:
        return pre

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=text)
    ])

    return response.content.strip().lower()
