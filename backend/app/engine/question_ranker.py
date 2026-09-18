class QuestionRanker:
    def score(self, candidate: dict, blueprint: dict, max_similarity: float) -> dict:
        # ... (keep this method exactly as it was) ...
        syllabus_relevance = 25
        historical_support = min((blueprint["historical_frequency"] / blueprint["total_papers"]) * 25, 25)
        study_material_support = 20

        pattern_score = 0
        if candidate.get("marks") in blueprint["preferred_marks"]:
            pattern_score += 7.5
        if candidate.get("question_type") in blueprint["question_types"]:
            pattern_score += 7.5

        difficulty_score = 10 if candidate.get("difficulty") == blueprint["difficulty"] else 5
        novelty = max(5 * (1 - max_similarity), 0)

        total = round(
            syllabus_relevance + historical_support + study_material_support +
            pattern_score + difficulty_score + novelty,
            1
        )

        return {
            "evidence_score": min(total, 100),
            "breakdown": {
                "syllabus_relevance": syllabus_relevance,
                "historical_support": round(historical_support, 1),
                "study_material_support": study_material_support,
                "pattern_compatibility": pattern_score,
                "difficulty_compatibility": difficulty_score,
                "novelty": round(novelty, 1),
            },
        }

    def explain(self, candidate: dict, blueprint: dict, breakdown: dict) -> str:
        """Builds a specific, human-readable evidence explanation for one question."""
        parts = []

        freq = blueprint["historical_frequency"]
        total = blueprint["total_papers"]
        years = blueprint["historical_years"]
        years_str = ", ".join(str(y) for y in years)

        if blueprint["recurrence_pattern"] == "consistent":
            parts.append(
                f"{blueprint['topic_name']} has appeared in {freq} of the last {total} papers "
                f"({years_str}) — one of the most consistently recurring topics in this subject."
            )
        elif blueprint["recurrence_pattern"] == "observed":
            parts.append(
                f"{blueprint['topic_name']} has been observed {freq} times across {total} papers "
                f"({years_str})."
            )
        else:
            parts.append(
                f"{blueprint['topic_name']} has appeared {freq} time(s) historically ({years_str})."
            )

        if candidate.get("marks") in blueprint["preferred_marks"]:
            parts.append(
                f"The {candidate.get('marks')}-mark weight matches this topic's typical mark allocation."
            )

        if candidate.get("question_type") in blueprint["question_types"]:
            parts.append(
                f"The '{candidate.get('question_type')}' format matches how this topic is usually tested."
            )

        if breakdown["novelty"] >= 4:
            parts.append("The question is phrased distinctly from any historical question on record.")

        return " ".join(parts)