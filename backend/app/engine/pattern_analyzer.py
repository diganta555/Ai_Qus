from collections import defaultdict


class PatternAnalyzer:
    def analyze(self, questions: list[dict], total_papers: int) -> list[dict]:
        """
        questions: list of dicts with keys:
          id, year, marks, question_type, topic_id, topic_name, unit_name,
          concept_id, repetition_type
        Returns: list of per-topic pattern dicts
        """
        by_topic: dict[int, list[dict]] = defaultdict(list)
        for q in questions:
            if q.get("topic_id"):
                by_topic[q["topic_id"]].append(q)

        results = []
        for topic_id, topic_questions in by_topic.items():
            years = sorted(set(q["year"] for q in topic_questions if q["year"]))

            marks_dist: dict[str, int] = defaultdict(int)
            for q in topic_questions:
                if q["marks"] is not None:
                    marks_dist[str(q["marks"])] += 1

            type_dist: dict[str, int] = defaultdict(int)
            for q in topic_questions:
                if q["question_type"]:
                    type_dist[q["question_type"]] += 1

            recurrence_intervals = [years[i + 1] - years[i] for i in range(len(years) - 1)]

            concept_ids = set(q["concept_id"] for q in topic_questions if q.get("concept_id"))

            exact_count = sum(1 for q in topic_questions if q.get("repetition_type") == "exact")
            near_count = sum(1 for q in topic_questions if q.get("repetition_type") == "near")

            results.append({
                "topic_id": topic_id,
                "topic_name": topic_questions[0]["topic_name"],
                "unit_name": topic_questions[0]["unit_name"],
                "frequency": len(years),
                "total_papers": total_papers,
                "years": years,
                "marks_distribution": dict(marks_dist),
                "question_types": dict(type_dist),
                "recurrence_intervals": recurrence_intervals,
                "concept_count": len(concept_ids),
                "exact_repeat_count": exact_count,
                "near_repeat_count": near_count,
            })

        # Sort by frequency (most recurring topics first)
        results.sort(key=lambda x: -x["frequency"])
        return results