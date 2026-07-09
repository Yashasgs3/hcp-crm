from langchain_groq import ChatGroq
from app.config.settings import settings

_llm = None


def get_llm():
    """Lazily initialize the Groq LLM client. Only created when first used."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.MODEL_NAME,
            temperature=0.2,
            max_tokens=2048,
        )
    return _llm
