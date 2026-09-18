from app.core.llm_factory import get_llm_with_fallback
from app.schemas.question import AskQuestionResponse


SYSTEM_PROMPT = """You are a helpful study assistant answering a student's question about their course material.

Rules:
- Answer using ONLY the provided context (study material excerpts and syllabus). Do not use outside knowledge beyond what's given.
- If the context does not contain enough information to answer confidently, say so clearly rather than guessing.
- Give a clear, well-structured answer suitable for exam preparation — use short paragraphs or bullet points where helpful.
- When the topic involves mathematical notation, write it using LaTeX syntax wrapped in $...$ for inline math or $$...$$ for display math.
- Keep the answer focused and not excessively long — a student should be able to read it quickly.
"""


class QAEngine:
    def __init__(self):
        self.llm = get_llm_with_fallback(AskQuestionResponse, temperature=0.3)

    def answer(self, question: str, context_chunks: list[str]) -> AskQuestionResponse:
        context_text = "\n\n---\n\n".join(context_chunks) if context_chunks else "No relevant context found."

        human_prompt = f"""Context from study material and syllabus:
{context_text}

Student's question: {question}

Answer the question using the context above."""

        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", human_prompt),
        ]
        return self.llm.invoke(messages)