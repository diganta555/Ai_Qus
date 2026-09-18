from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.schemas.question import TopicClassificationBatch
from app.core.llm_factory import get_llm_with_fallback
from app.schemas.question import TopicClassificationBatch


SYSTEM_PROMPT = """You are an expert at mapping exam questions to a course syllabus structure.

You will be given:
1. A syllabus structure of Units, each containing Topics.
2. A batch of extracted exam questions, each with a question_id.

For EACH question, determine which single syllabus Topic it best matches (and that topic's parent Unit name).

Rules:
- Only match to topics that actually exist in the given syllabus structure — do not invent topic names.
- If a question could reasonably fit more than one topic, choose the single best match.
- If a question does not fit any topic in the syllabus (e.g. it is an instruction like "answer any five"), set matched_unit_name and matched_topic_name to null and confidence to "no_match".
- confidence should be "high" if the match is clear and direct, "medium" if reasonably inferred, "low" if it's a weak/uncertain guess.
- Return one classification per question_id given, in the same order.
"""


class TopicClassifier:
    def __init__(self):
        self.llm = get_llm_with_fallback(TopicClassificationBatch, temperature=0)

    def classify_batch(self, syllabus_structure: dict, questions: list[dict]) -> TopicClassificationBatch:
        questions_text = "\n".join(
            f"question_id={q['id']}: {q['question_text']}" for q in questions
        )
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", f"Syllabus structure:\n{syllabus_structure}\n\nQuestions:\n{questions_text}"),
        ]
        return self.llm.invoke(messages)