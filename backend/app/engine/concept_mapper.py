from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.schemas.question import ConceptMappingResult
from app.core.llm_factory import get_llm_with_fallback
from app.schemas.question import ConceptMappingResult


SYSTEM_PROMPT = """You are an expert at identifying when different exam questions test the same underlying academic concept, even if worded differently.

You will be given a batch of exam questions (all already known to belong to the same syllabus topic), each with a question_id.

Group questions that test the same specific concept together, even across different years and different wording.
Examples of the same concept: "Explain AVL tree rotations" and "Describe AVL balancing operations" and "Explain LL, RR, LR, RL rotations" all belong to concept "AVL Tree Rotations".

Rules:
- Give each concept group a short, clear concept_name (a few words).
- A question can belong to only one concept group.
- Only group questions that are truly testing the same concept — do not force unrelated questions together.
- If a question is unique with no matches, it still needs its own concept group (with just that one question_id).
- Every question_id given to you must appear in exactly one group.
"""


class ConceptMapper:
    def __init__(self):
        self.llm = get_llm_with_fallback(ConceptMappingResult, temperature=0)

    def map_concepts(self, questions: list[dict]) -> ConceptMappingResult:
        questions_text = "\n".join(
            f"question_id={q['id']}: {q['question_text']}" for q in questions
        )
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", f"Questions:\n{questions_text}"),
        ]
        return self.llm.invoke(messages)