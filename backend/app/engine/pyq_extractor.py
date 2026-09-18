from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.schemas.question import ExtractedQuestionsResult
from app.core.llm_factory import get_llm_with_fallback
from app.schemas.question import ExtractedQuestionsResult

SYSTEM_PROMPT = """You are an expert at reading university previous-year exam question papers.
Given the raw text of one exam paper, extract every individual question asked.

Rules:
- Determine the exam year from the paper's text itself (e.g. from a header, date, or "Examination, YYYY" line) — do not guess if it is not stated.
- Extract every question, including sub-parts, as separate entries where marks are given separately; otherwise keep multi-part questions as one entry.
- question_number should reflect the number printed on the paper (e.g. 1, 2, 3...). Use null if not numbered.
- marks should be the numeric marks allotted, if stated. Use null if not stated.
- question_type should be one of: "descriptive", "problem_solving", "mcq", "short_answer" — infer from phrasing. Use your best judgement.
- Do not include instructions, headers, or non-question text as questions.
- Preserve the original question wording as closely as possible; only clean up obvious OCR/formatting noise.
"""


class PYQExtractor:
    def __init__(self):
        self.llm = get_llm_with_fallback(ExtractedQuestionsResult, temperature=0)

    def extract(self, paper_text: str) -> ExtractedQuestionsResult:
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", f"Exam paper text:\n\n{paper_text}"),
        ]
        return self.llm.invoke(messages)