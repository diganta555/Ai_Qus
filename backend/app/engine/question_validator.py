from sentence_transformers import SentenceTransformer
import numpy as np


class QuestionValidator:
    def __init__(self, duplicate_threshold: float = 0.88):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = duplicate_threshold

    def check_duplicate(self, candidate_text: str, existing_texts: list[str]) -> tuple[bool, float]:
        """Returns (is_duplicate, max_similarity_score)"""
        if not existing_texts:
            return False, 0.0

        candidate_emb = self.model.encode([candidate_text], normalize_embeddings=True)
        existing_embs = self.model.encode(existing_texts, normalize_embeddings=True)
        similarities = np.dot(candidate_emb, existing_embs.T)[0]
        max_sim = float(np.max(similarities))
        return max_sim >= self.threshold, max_sim

    def validate(self, candidate: dict, historical_pyq_texts: list[str], min_length: int = 15) -> dict:
        """
        candidate: {"question_text": str, "marks": int, ...}
        Returns: {"is_valid": bool, "rejection_reason": str | None, "max_similarity": float}
        """
        text = candidate["question_text"].strip()

        # 1. Basic quality check
        if len(text) < min_length:
            return {"is_valid": False, "rejection_reason": "Question text too short/malformed", "max_similarity": 0.0}

        if not text.endswith(("?", ".", ":")):
            # Not a hard rule-breaker, just a soft signal — still allow it, many valid questions don't end in punctuation cleanly
            pass

        # 2. Duplicate check against historical PYQs
        is_dup, max_sim = self.check_duplicate(text, historical_pyq_texts)
        if is_dup:
            return {
                "is_valid": False,
                "rejection_reason": f"Too similar to an existing historical question (similarity={max_sim:.2f})",
                "max_similarity": max_sim,
            }

        # 3. Marks sanity check
        if candidate.get("marks") is not None and (candidate["marks"] <= 0 or candidate["marks"] > 30):
            return {"is_valid": False, "rejection_reason": "Marks value out of reasonable range", "max_similarity": max_sim}

        return {"is_valid": True, "rejection_reason": None, "max_similarity": max_sim}