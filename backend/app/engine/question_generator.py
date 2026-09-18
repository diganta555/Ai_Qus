from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.schemas.question import GeneratedQuestionsBatch
from app.core.llm_factory import get_llm_with_fallback
from app.schemas.question import GeneratedQuestionsBatch

SYSTEM_PROMPT = """You are an expert university exam paper setter.
Generate NEW exam questions for a topic, based on the syllabus, historical exam patterns, and academic context provided.

Rules:
- Generate questions that fit the SAME style, difficulty, and format as the historical questions shown, but do NOT copy any historical question verbatim.
- Stay strictly within the topic and syllabus scope given — do not introduce content not covered.
- IMPORTANT: Vary the marks across the batch of questions you generate. Use a MIX of the different mark values given in "Preferred marks" below — do not assign the same mark value to every question. A short factual question should carry fewer marks (e.g. 2); a question requiring derivation, proof, or multi-step problem-solving should carry more marks (e.g. 10).
- Similarly, vary the question_type across the batch where the blueprint lists more than one preferred type — don't make every question the same type.
- Ground each question in the academic context provided (it should be answerable using that material).
- Vary the phrasing and specific scenario/numbers used compared to historical questions, while testing the same underlying concept.
- Generate exactly the number of questions requested.
"""


class QuestionGenerator:
    def __init__(self):
        self.llm = get_llm_with_fallback(GeneratedQuestionsBatch, temperature=0.7)

    def generate(self, blueprint: dict, academic_context: list[str], historical_pyqs: list[str], num_questions: int = 4) -> GeneratedQuestionsBatch:
        context_text = "\n\n".join(academic_context) if academic_context else "No academic context available."
        pyqs_text = "\n".join(f"- {q}" for q in historical_pyqs) if historical_pyqs else "None available."

        human_prompt = f"""Topic: {blueprint['topic_name']} (Unit: {blueprint['unit_name']})
Preferred marks (use a mix of these across your questions, not just one value): {blueprint['preferred_marks']}
Preferred question types: {blueprint['question_types']}
Difficulty: {blueprint['difficulty']}
Historical frequency: appeared in {blueprint['historical_frequency']} of {blueprint['total_papers']} papers

Academic context (from textbook/study material):
{context_text}

Historical questions asked on this topic (for style reference only — do not copy):
{pyqs_text}

Generate {num_questions} new exam questions for this topic, using a varied mix of the preferred marks and question types listed above."""

        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", human_prompt),
        ]
        return self.llm.invoke(messages)