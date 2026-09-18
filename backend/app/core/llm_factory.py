from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.core.config import settings


# Groq model choice: fast, strong instruction-following, good for structured output
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENAI_MODEL = "gpt-4o-mini"


def get_llm_with_fallback(structured_schema, temperature: float = 0):
    """
    Returns a LangChain-compatible object that tries Groq first, and automatically
    falls back to OpenAI if the Groq call fails (rate limit, outage, bad response, etc.).
    Both are wrapped with the same structured_output schema so calling code doesn't change.
    """
    primary = None
    fallback = None

    if settings.groq_api_key:
        primary = ChatGroq(
            model=GROQ_MODEL,
            api_key=settings.groq_api_key,
            temperature=temperature,
        ).with_structured_output(structured_schema)

    if settings.openai_api_key:
        fallback = ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=settings.openai_api_key,
            temperature=temperature,
        ).with_structured_output(structured_schema)

    if primary is None and fallback is None:
        raise ValueError("No LLM API key configured — set GROQ_API_KEY or OPENAI_API_KEY in .env")

    if primary is None:
        return fallback  # only OpenAI configured
    if fallback is None:
        return primary   # only Groq configured

    # LangChain's built-in fallback chaining — tries primary, falls back to fallback on any exception
    return primary.with_fallbacks([fallback])