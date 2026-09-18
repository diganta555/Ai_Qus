from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.schemas.syllabus import SyllabusStructure
from app.core.llm_factory import get_llm_with_fallback
from app.schemas.syllabus import SyllabusStructure


SYSTEM_PROMPT = """..."""  # keep exactly as-is


class SyllabusAnalyzer:
    def __init__(self):
        self.llm = get_llm_with_fallback(SyllabusStructure, temperature=0)

    def analyze(self, syllabus_text: str) -> SyllabusStructure:
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", f"Syllabus text:\n\n{syllabus_text}"),
        ]
        return self.llm.invoke(messages)


SYSTEM_PROMPT = """You are an expert academic syllabus parser.
Given the raw text of a university course syllabus, extract its structure as
Units, each containing Topics, each optionally containing Subtopics.

Rules:
- Preserve the unit numbering and names as given in the syllabus.
- Break each unit's content into distinct topics.
- Only include subtopics when the syllabus text clearly lists them; otherwise leave the subtopics list empty.
- Do not invent content that is not present in the syllabus text.
"""

class SyllabusAnalyzer:
    def __init__(self):
        self.llm = get_llm_with_fallback(SyllabusStructure, temperature=0)

    def analyze(self, syllabus_text: str) -> SyllabusStructure:
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", f"Syllabus text:\n\n{syllabus_text}"),
        ]
        return self.llm.invoke(messages)