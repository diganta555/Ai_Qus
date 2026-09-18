from sentence_transformers import SentenceTransformer
import numpy as np


class RepetitionAnalyzer:
    def __init__(self, near_duplicate_threshold: float = 0.85):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = near_duplicate_threshold

    def _normalize(self, text: str) -> str:
        return " ".join(text.lower().split())

    def analyze(self, questions: list[dict]) -> list[dict]:
        """
        questions: list of {id, question_text, concept_id}
        Returns: list of {id, repetition_type, repetition_group_id}
        """
        if len(questions) < 2:
            return []

        texts = [q["question_text"] for q in questions]
        normalized = [self._normalize(t) for t in texts]

        # 1. Exact repeats: identical normalized text
        exact_groups: dict[str, list[int]] = {}
        for q, norm in zip(questions, normalized):
            exact_groups.setdefault(norm, []).append(q["id"])

        results = {}
        group_counter = 1
        exact_matched_ids = set()

        for norm, ids in exact_groups.items():
            if len(ids) > 1:
                for qid in ids:
                    results[qid] = {"repetition_type": "exact", "repetition_group_id": group_counter}
                    exact_matched_ids.add(qid)
                group_counter += 1

        # 2. Near repeats: embedding cosine similarity (skip questions already marked exact)
        remaining = [q for q in questions if q["id"] not in exact_matched_ids]
        if len(remaining) >= 2:
            embeddings = self.model.encode([q["question_text"] for q in remaining], normalize_embeddings=True)
            sim_matrix = np.dot(embeddings, embeddings.T)

            visited = set()
            for i, q in enumerate(remaining):
                if q["id"] in visited:
                    continue
                group_ids = [q["id"]]
                for j in range(i + 1, len(remaining)):
                    other = remaining[j]
                    if other["id"] in visited:
                        continue
                    if sim_matrix[i][j] >= self.threshold:
                        group_ids.append(other["id"])
                        visited.add(other["id"])
                if len(group_ids) > 1:
                    for qid in group_ids:
                        results[qid] = {"repetition_type": "near", "repetition_group_id": group_counter}
                        visited.add(qid)
                    group_counter += 1

        # 3. Concept repeats: same concept_id, not already exact/near, and concept has 2+ questions
        concept_groups: dict[int, list[int]] = {}
        for q in questions:
            if q["id"] in results:
                continue
            if q.get("concept_id"):
                concept_groups.setdefault(q["concept_id"], []).append(q["id"])

        for concept_id, ids in concept_groups.items():
            if len(ids) > 1:
                for qid in ids:
                    results[qid] = {"repetition_type": "concept", "repetition_group_id": group_counter}
                group_counter += 1

        return [{"id": qid, **data} for qid, data in results.items()]