from app.core.llm_factory import get_llm_with_fallback
from app.schemas.question import AnswerResult


SYSTEM_PROMPT = """You are an expert academic answering exam questions for a student.

You will be given a question and relevant context from the student's own study material.

Rules:
- Answer using the provided context as your primary source. You may use well-established general knowledge to fill gaps, but never contradict the context.
- Give a complete, well-structured answer appropriate for the question's mark value — a 2-mark question needs a concise answer, a 10-mark question needs a thorough, structured one with steps/derivation where relevant.
- When the answer involves mathematical notation, write it using LaTeX syntax wrapped in $...$ for inline math or $$...$$ for display math.
- For problem-solving or numerical questions, show the working/steps, not just the final result.
- Do not restate the question back at the start of the answer — start directly with the answer content.
"""


class AnswerGenerator:
    def __init__(self):
        self.llm = get_llm_with_fallback(AnswerResult, temperature=0.2)

    def generate(self, question_text: str, marks: int | None, context_chunks: list[str]) -> AnswerResult:
        context_text = "\n\n---\n\n".join(context_chunks) if context_chunks else "No specific context available — use general subject knowledge."

        human_prompt = f"""Question ({marks or 'unspecified'} marks): {question_text}

Relevant context from study material:
{context_text}

Write the answer to this question."""

        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", human_prompt),
        ]
        return self.llm.invoke(messages)
