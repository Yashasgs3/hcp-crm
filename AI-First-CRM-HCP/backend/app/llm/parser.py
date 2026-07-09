import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.groq_client import get_llm
from app.prompts.interaction_prompt import SYSTEM_PROMPT


def extract_interaction(conversation: str):

    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=conversation),
    ]

    response = llm.invoke(messages)

    content = response.content.strip()

    # Strip markdown code fences if present
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove opening fence line
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove closing fence line
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    try:
        data = json.loads(content)
        return data

    except Exception:

        return {
            "summary": response.content
        }
