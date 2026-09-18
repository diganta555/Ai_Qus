class BlueprintBuilder:
    def _classify_recurrence(self, frequency: int, total_papers: int) -> str:
        ratio = frequency / total_papers if total_papers else 0
        if ratio >= 0.85:
            return "consistent"        # appears in almost every paper
        elif ratio >= 0.5:
            return "observed"          # appears in about half or more
        elif ratio >= 0.25:
            return "occasional"        # appears sometimes
        else:
            return "rare"

    def _pick_preferred_marks(self, marks_distribution: dict[str, int], top_n: int = 5) -> list[int]:
        # Sort marks by how often they appear, take the most common ones
        sorted_marks = sorted(marks_distribution.items(), key=lambda x: -x[1])
        return [int(m) for m, _ in sorted_marks[:top_n]]

    def _pick_question_types(self, type_distribution: dict[str, int], top_n: int = 3) -> list[str]:
        sorted_types = sorted(type_distribution.items(), key=lambda x: -x[1])
        return [t for t, _ in sorted_types[:top_n]]

    def _estimate_difficulty(self, marks_distribution: dict[str, int]) -> str:
        # Rough heuristic: higher average marks -> higher difficulty
        total_weighted = sum(int(m) * count for m, count in marks_distribution.items())
        total_count = sum(marks_distribution.values())
        if total_count == 0:
            return "medium"
        avg_marks = total_weighted / total_count
        if avg_marks <= 3:
            return "easy"
        elif avg_marks <= 7:
            return "medium"
        else:
            return "hard"

    def _evidence_strength(self, frequency: int, total_papers: int, concept_count: int,
                            exact_repeat_count: int, near_repeat_count: int) -> float:
        # Simple weighted score, capped at 100 — refined later by the actual Ranker (Step 17)
        freq_score = (frequency / total_papers) * 60 if total_papers else 0
        repeat_score = min((exact_repeat_count * 5 + near_repeat_count * 2), 25)
        concept_score = min(concept_count * 3, 15)
        return round(min(freq_score + repeat_score + concept_score, 100), 1)

    def build(self, pattern: dict) -> dict:
        """
        pattern: one topic's pattern dict, as produced by PatternAnalyzer (Step 11)
        """
        recurrence = self._classify_recurrence(pattern["frequency"], pattern["total_papers"])
        preferred_marks = self._pick_preferred_marks(pattern["marks_distribution"])
        question_types = self._pick_question_types(pattern["question_types"])
        difficulty = self._estimate_difficulty(pattern["marks_distribution"])
        evidence_strength = self._evidence_strength(
            pattern["frequency"],
            pattern["total_papers"],
            pattern["concept_count"],
            pattern["exact_repeat_count"],
            pattern["near_repeat_count"],
        )

        return {
            "topic_id": pattern["topic_id"],
            "topic_name": pattern["topic_name"],
            "unit_name": pattern["unit_name"],
            "historical_frequency": pattern["frequency"],
            "total_papers": pattern["total_papers"],
            "historical_years": pattern["years"],
            "preferred_marks": preferred_marks or [10],
            "question_types": question_types or ["descriptive"],
            "difficulty": difficulty,
            "recurrence_pattern": recurrence,
            "evidence_strength": evidence_strength,
        }