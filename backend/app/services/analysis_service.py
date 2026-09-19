import re
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.syllabus import SyllabusUnit, SyllabusTopic, SyllabusSubtopic
from app.engine.document_processor import DocumentProcessor
from app.engine.syllabus_analyzer import SyllabusAnalyzer
from app.models.question import ExtractedQuestion
from app.engine.pyq_extractor import PYQExtractor
from app.engine.topic_classifier import TopicClassifier
from app.models.concept import Concept
from app.engine.concept_mapper import ConceptMapper
from app.engine.repetition_analyzer import RepetitionAnalyzer
from app.engine.rag_engine import RAGEngine
from app.engine.blueprint_builder import BlueprintBuilder

from app.models.generated_question import GeneratedQuestion
from app.engine.question_generator import QuestionGenerator
from app.engine.question_validator import QuestionValidator
from app.engine.question_ranker import QuestionRanker
from app.engine.qa_engine import QAEngine
import uuid
from datetime import datetime
from app.engine.answer_generator import AnswerGenerator


import json
from app.models.pattern import TopicPatternRecord
from app.engine.pattern_analyzer import PatternAnalyzer
from app.models.syllabus import SyllabusTopic, SyllabusUnit


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.processor = DocumentProcessor()
        self.syllabus_analyzer = SyllabusAnalyzer()
        self.pyq_extractor = PYQExtractor()
        self.topic_classifier = TopicClassifier()
        self.concept_mapper = ConceptMapper()
        self.repetition_analyzer = RepetitionAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        self.rag_engine = RAGEngine()
        self.blueprint_builder = BlueprintBuilder()
        self.question_generator = QuestionGenerator()
        self.question_validator = QuestionValidator()
        self.question_ranker = QuestionRanker()
        self.qa_engine = QAEngine()
        self.answer_generator = AnswerGenerator()

    def analyze_syllabus(self, subject_id: int) -> dict:
        document = (
            self.db.query(Document)
            .filter(Document.subject_id == subject_id, Document.document_type == "syllabus")
            .first()
        )
        if not document:
            raise ValueError("No syllabus document found for this subject")

        # 1. Extract clean text
        result = self.processor.process(document.file_path)
        cleaned_text = result["cleaned_text"]

        # 2. Run LLM structure extraction
        structure = self.syllabus_analyzer.analyze(cleaned_text)

        # 3. Clear any previous syllabus structure for this subject (allow re-analysis)
        existing_units = self.db.query(SyllabusUnit).filter(SyllabusUnit.subject_id == subject_id).all()
        for unit in existing_units:
            topics = self.db.query(SyllabusTopic).filter(SyllabusTopic.unit_id == unit.id).all()
            for topic in topics:
                self.db.query(SyllabusSubtopic).filter(SyllabusSubtopic.topic_id == topic.id).delete()
            self.db.query(SyllabusTopic).filter(SyllabusTopic.unit_id == unit.id).delete()
        self.db.query(SyllabusUnit).filter(SyllabusUnit.subject_id == subject_id).delete()
        self.db.commit()

        # 4. Persist new structure
        for unit in structure.units:
            db_unit = SyllabusUnit(
                subject_id=subject_id,
                unit_number=unit.unit_number,
                unit_name=unit.unit_name,
            )
            self.db.add(db_unit)
            self.db.flush()  # get db_unit.id before commit

            for topic in unit.topics:
                db_topic = SyllabusTopic(unit_id=db_unit.id, topic_name=topic.name)
                self.db.add(db_topic)
                self.db.flush()

                for subtopic_name in topic.subtopics:
                    db_subtopic = SyllabusSubtopic(topic_id=db_topic.id, subtopic_name=subtopic_name)
                    self.db.add(db_subtopic)

        self.db.commit()
        return structure.model_dump()
    
    def extract_pyqs(self, subject_id: int) -> dict:
        pyq_documents = (
            self.db.query(Document)
            .filter(Document.subject_id == subject_id, Document.document_type == "previous_year_question")
            .all()
        )
        if not pyq_documents:
            raise ValueError("No previous-year-question documents found for this subject")

        self.db.query(ExtractedQuestion).filter(ExtractedQuestion.subject_id == subject_id).delete()
        self.db.commit()

        total_saved = 0
        per_document_results = []

        for document in pyq_documents:
            result = self.processor.process(document.file_path)
            extraction = self.pyq_extractor.extract(result["cleaned_text"])

            # Fallback: if the LLM couldn't find a year in the text, try the filename
            resolved_year = extraction.year
            if resolved_year is None:
                match = re.search(r"(20\d{2})", document.file_name)
                if match:
                    resolved_year = int(match.group(1))

            for q in extraction.questions:
                db_question = ExtractedQuestion(
                    subject_id=subject_id,
                    document_id=document.id,
                    year=resolved_year,
                    question_number=q.question_number,
                    question_text=q.question_text,
                    marks=q.marks,
                    question_type=q.question_type,
                )
                self.db.add(db_question)
                total_saved += 1

            per_document_results.append({
                "file_name": document.file_name,
                "detected_year": resolved_year,
                "questions_found": len(extraction.questions),
            })

        self.db.commit()
        return {
            "total_questions_saved": total_saved,
            "documents_processed": per_document_results,
        }
        
    def classify_topics(self, subject_id: int, batch_size: int = 20) -> dict:
        # Build syllabus structure dict (topic_name -> topic_id, unit_name -> unit lookup)
        units = self.db.query(SyllabusUnit).filter(SyllabusUnit.subject_id == subject_id).all()
        if not units:
            raise ValueError("No syllabus structure found — run analyze-syllabus first")

        syllabus_dict = {"units": []}
        topic_lookup = {}  # (unit_name, topic_name) -> topic_id

        for unit in units:
            topics = self.db.query(SyllabusTopic).filter(SyllabusTopic.unit_id == unit.id).all()
            topic_names = []
            for topic in topics:
                topic_names.append(topic.topic_name)
                topic_lookup[(unit.unit_name, topic.topic_name)] = topic.id
            syllabus_dict["units"].append({"unit_name": unit.unit_name, "topics": topic_names})

        # Get all extracted questions for this subject
        questions = self.db.query(ExtractedQuestion).filter(ExtractedQuestion.subject_id == subject_id).all()
        if not questions:
            raise ValueError("No extracted questions found — run extract-pyqs first")

        matched_count = 0
        unmatched_count = 0

        # Process in batches
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            batch_dicts = [{"id": q.id, "question_text": q.question_text} for q in batch]

            result = self.topic_classifier.classify_batch(syllabus_dict, batch_dicts)

            for classification in result.classifications:
                question = next((q for q in batch if q.id == classification.question_id), None)
                if not question:
                    continue

                if classification.matched_unit_name and classification.matched_topic_name:
                    topic_id = topic_lookup.get(
                        (classification.matched_unit_name, classification.matched_topic_name)
                    )
                    if topic_id:
                        question.topic_id = topic_id
                        matched_count += 1
                    else:
                        unmatched_count += 1
                else:
                    unmatched_count += 1

        self.db.commit()
        return {
            "total_questions": len(questions),
            "matched": matched_count,
            "unmatched": unmatched_count,
        }
        
    def map_concepts(self, subject_id: int) -> dict:
        # Clear existing concepts for this subject (allow re-mapping)
        self.db.query(Concept).filter(Concept.subject_id == subject_id).delete()
        self.db.commit()

        # Get all classified questions (must have a topic_id), grouped by topic
        questions = (
            self.db.query(ExtractedQuestion)
            .filter(ExtractedQuestion.subject_id == subject_id, ExtractedQuestion.topic_id.isnot(None))
            .all()
        )
        if not questions:
            raise ValueError("No topic-classified questions found — run classify-topics first")

        # Group question objects by topic_id
        questions_by_topic: dict[int, list] = {}
        for q in questions:
            questions_by_topic.setdefault(q.topic_id, []).append(q)

        total_concepts = 0

        for topic_id, topic_questions in questions_by_topic.items():
            if len(topic_questions) == 1:
                # Single question — no need to call the LLM, just make it its own concept
                q = topic_questions[0]
                concept = Concept(
                    subject_id=subject_id,
                    concept_name=q.question_text[:60],
                    topic_id=topic_id,
                )
                self.db.add(concept)
                self.db.flush()
                q.concept_id = concept.id
                total_concepts += 1
                continue

            batch_dicts = [{"id": q.id, "question_text": q.question_text} for q in topic_questions]
            result = self.concept_mapper.map_concepts(batch_dicts)

            for group in result.concepts:
                concept = Concept(
                    subject_id=subject_id,
                    concept_name=group.concept_name,
                    topic_id=topic_id,
                    description=group.description,
                )
                self.db.add(concept)
                self.db.flush()  # get concept.id

                for qid in group.question_ids:
                    matched_q = next((q for q in topic_questions if q.id == qid), None)
                    if matched_q:
                        matched_q.concept_id = concept.id

                total_concepts += 1

        self.db.commit()
        return {
            "total_concepts_created": total_concepts,
            "topics_processed": len(questions_by_topic),
        }

    def analyze_repetition(self, subject_id: int) -> dict:
        questions = (
            self.db.query(ExtractedQuestion)
            .filter(ExtractedQuestion.subject_id == subject_id)
            .all()
        )
        if not questions:
            raise ValueError("No extracted questions found — run extract-pyqs first")

        # Reset previous repetition tags
        for q in questions:
            q.repetition_type = None
            q.repetition_group_id = None
        self.db.commit()

        question_dicts = [
            {"id": q.id, "question_text": q.question_text, "concept_id": q.concept_id}
            for q in questions
        ]
        results = self.repetition_analyzer.analyze(question_dicts)

        by_id = {q.id: q for q in questions}
        counts = {"exact": 0, "near": 0, "concept": 0}

        for r in results:
            q = by_id.get(r["id"])
            if q:
                q.repetition_type = r["repetition_type"]
                q.repetition_group_id = r["repetition_group_id"]
                counts[r["repetition_type"]] += 1

        self.db.commit()
        return {
            "total_questions": len(questions),
            "exact_repeats": counts["exact"],
            "near_repeats": counts["near"],
            "concept_repeats": counts["concept"],
        }
        
    def analyze_patterns(self, subject_id: int) -> dict:
        questions = (
            self.db.query(ExtractedQuestion)
            .filter(ExtractedQuestion.subject_id == subject_id, ExtractedQuestion.topic_id.isnot(None))
            .all()
        )
        if not questions:
            raise ValueError("No topic-classified questions found — run classify-topics first")

        total_papers = (
            self.db.query(Document)
            .filter(Document.subject_id == subject_id, Document.document_type == "previous_year_question")
            .count()
        )

        # Build enriched dicts with topic/unit names
        question_dicts = []
        for q in questions:
            topic = self.db.query(SyllabusTopic).filter(SyllabusTopic.id == q.topic_id).first()
            unit_name = None
            if topic:
                unit = self.db.query(SyllabusUnit).filter(SyllabusUnit.id == topic.unit_id).first()
                unit_name = unit.unit_name if unit else None
            question_dicts.append({
                "id": q.id,
                "year": q.year,
                "marks": q.marks,
                "question_type": q.question_type,
                "topic_id": q.topic_id,
                "topic_name": topic.topic_name if topic else "Unknown",
                "unit_name": unit_name or "Unknown",
                "concept_id": q.concept_id,
                "repetition_type": q.repetition_type,
            })

        patterns = self.pattern_analyzer.analyze(question_dicts, total_papers)

        # Clear old records and save new ones
        self.db.query(TopicPatternRecord).filter(TopicPatternRecord.subject_id == subject_id).delete()
        self.db.commit()

        for p in patterns:
            record = TopicPatternRecord(
                subject_id=subject_id,
                topic_id=p["topic_id"],
                topic_name=p["topic_name"],
                unit_name=p["unit_name"],
                frequency=p["frequency"],
                total_papers=p["total_papers"],
                years_json=json.dumps(p["years"]),
                marks_distribution_json=json.dumps(p["marks_distribution"]),
                question_types_json=json.dumps(p["question_types"]),
                recurrence_intervals_json=json.dumps(p["recurrence_intervals"]),
                concept_count=p["concept_count"],
                exact_repeat_count=p["exact_repeat_count"],
                near_repeat_count=p["near_repeat_count"],
            )
            self.db.add(record)

        self.db.commit()
        return {
            "total_papers_analyzed": total_papers,
            "topics_analyzed": len(patterns),
        }

    def build_knowledge_base(self, subject_id: int) -> dict:
        chunks = []

        # 1. Study material chunks
        study_docs = (
            self.db.query(Document)
            .filter(Document.subject_id == subject_id, Document.document_type == "study_material")
            .all()
        )
        for doc in study_docs:
            result = self.processor.process(doc.file_path)
            for i, chunk_text in enumerate(result["chunks"]):
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "subject_id": subject_id,
                        "document_type": "study_material",
                        "document_id": doc.id,
                        "file_name": doc.file_name,
                        "chunk_index": i,
                    },
                })

        # 2. Syllabus chunks
        syllabus_docs = (
            self.db.query(Document)
            .filter(Document.subject_id == subject_id, Document.document_type == "syllabus")
            .all()
        )
        for doc in syllabus_docs:
            result = self.processor.process(doc.file_path)
            for i, chunk_text in enumerate(result["chunks"]):
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "subject_id": subject_id,
                        "document_type": "syllabus",
                        "document_id": doc.id,
                        "file_name": doc.file_name,
                        "chunk_index": i,
                    },
                })

        # 3. ALL previous-year questions (one chunk per question, with rich metadata)
        pyq_questions = (
            self.db.query(ExtractedQuestion)
            .filter(ExtractedQuestion.subject_id == subject_id)
            .all()
        )
        for q in pyq_questions:
            topic_name = None
            if q.topic_id:
                topic = self.db.query(SyllabusTopic).filter(SyllabusTopic.id == q.topic_id).first()
                topic_name = topic.topic_name if topic else None

            chunks.append({
                "text": q.question_text,
                "metadata": {
                    "subject_id": subject_id,
                    "document_type": "previous_year_question",
                    "question_id": q.id,
                    "year": q.year,
                    "topic": topic_name,
                    "marks": q.marks,
                    "question_type": q.question_type,
                    "concept_id": q.concept_id,
                },
            })

        if not chunks:
            raise ValueError("No documents or questions found to build a knowledge base")

        result = self.rag_engine.build_index(subject_id, chunks)
        return result
    
    def build_blueprints(self, subject_id: int) -> list[dict]:
        records = (
            self.db.query(TopicPatternRecord)
            .filter(TopicPatternRecord.subject_id == subject_id)
            .all()
        )
        if not records:
            raise ValueError("No pattern data found — run analyze-patterns first")

        blueprints = []
        for r in records:
            pattern = {
                "topic_id": r.topic_id,
                "topic_name": r.topic_name,
                "unit_name": r.unit_name,
                "frequency": r.frequency,
                "total_papers": r.total_papers,
                "years": json.loads(r.years_json),
                "marks_distribution": json.loads(r.marks_distribution_json),
                "question_types": json.loads(r.question_types_json),
                "concept_count": r.concept_count,
                "exact_repeat_count": r.exact_repeat_count,
                "near_repeat_count": r.near_repeat_count,
            }
            blueprint = self.blueprint_builder.build(pattern)
            blueprints.append(blueprint)

        # Sort by evidence strength, strongest first
        blueprints.sort(key=lambda b: -b["evidence_strength"])
        return blueprints
    
    def generate_questions(self, subject_id: int, num_topics: int = 8, questions_per_topic: int = 4, final_top_n: int = 20) -> dict:
        blueprints = self.build_blueprints(subject_id)
        if not blueprints:
            raise ValueError("No blueprints available — run analyze-patterns first")

        top_blueprints = blueprints[:num_topics]

        batch_number = (
            self.db.query(GeneratedQuestion.batch_id)
            .filter(GeneratedQuestion.subject_id == subject_id)
            .distinct()
            .count()
        ) + 1
        batch_id = f"batch_{batch_number}"
        all_candidates = []

        for blueprint in top_blueprints:
            # 1. Retrieve RAG context for this topic
            rag_result = self.rag_engine.retrieve_for_topic(subject_id, blueprint["topic_name"], top_k=5)
            academic_texts = [r["text"] for r in rag_result["academic_context"]]
            historical_texts = [r["text"] for r in rag_result["historical_pyqs"]]

            # 2. Generate candidates
            try:
                batch = self.question_generator.generate(
                    blueprint, academic_texts, historical_texts, num_questions=questions_per_topic
                )
            except Exception:
                continue  # skip this topic if generation fails, don't kill the whole run

            # 3. Validate + score each candidate
            for item in batch.questions:
                candidate = {
                    "question_text": item.question_text,
                    "marks": item.marks,
                    "difficulty": item.difficulty,
                    "question_type": item.question_type,
                }
                validation = self.question_validator.validate(candidate, historical_texts)

                if not validation["is_valid"]:
                    all_candidates.append({
                        **candidate,
                        "topic_id": blueprint["topic_id"],
                        "topic_name": blueprint["topic_name"],
                        "status": "rejected",
                        "rejection_reason": validation["rejection_reason"],
                        "evidence_score": 0,
                        "evidence_breakdown": None,
                        "generation_reason": None,
                        "supporting_years": blueprint["historical_years"],
                    })
                    continue

                score_result = self.question_ranker.score(candidate, blueprint, validation["max_similarity"])
                explanation = self.question_ranker.explain(candidate, blueprint, score_result["breakdown"])
                all_candidates.append({
                    **candidate,
                    "topic_id": blueprint["topic_id"],
                    "topic_name": blueprint["topic_name"],
                    "status": "valid",
                    "rejection_reason": None,
                    "evidence_score": score_result["evidence_score"],
                    "evidence_breakdown": score_result["breakdown"],
                    "generation_reason": explanation,
                    "supporting_years": blueprint["historical_years"],
                })

        # 4. Rank: sort valid candidates by evidence_score, mark top N as "ranked"
        valid_candidates = [c for c in all_candidates if c["status"] == "valid"]
        valid_candidates.sort(key=lambda c: -c["evidence_score"])

        for i, c in enumerate(valid_candidates):
            if i < final_top_n:
                c["status"] = "ranked"
                
        # # Generate answers only for the final ranked questions (not all candidates)
        # for c in valid_candidates:
        #     if c["status"] != "ranked":
        #         continue
        #     try:
        #         rag_result = self.rag_engine.retrieve_for_topic(subject_id, c["topic_name"], top_k=4)
        #         context_texts = [r["text"] for r in rag_result["academic_context"]]
        #         answer = self.answer_generator.generate(c["question_text"], c.get("marks"), context_texts)
        #         c["answer_text"] = answer.answer_text
        #     except Exception:
        #         c["answer_text"] = None

        # 5. Persist everything (candidates, rejected, and ranked) for transparency
        for c in all_candidates:
            record = GeneratedQuestion(
                subject_id=subject_id,
                batch_id=batch_id,
                question_text=c["question_text"],
                answer_text=c.get("answer_text"),
                topic_id=c["topic_id"],
                topic_name=c["topic_name"],
                marks=c.get("marks"),
                difficulty=c.get("difficulty"),
                question_type=c.get("question_type"),
                evidence_score=c["evidence_score"],
                evidence_breakdown=json.dumps(c["evidence_breakdown"]) if c.get("evidence_breakdown") else None,
                generation_reason=c.get("generation_reason"),
                supporting_years=json.dumps(c["supporting_years"]),
                status=c["status"],
                rejection_reason=c.get("rejection_reason"),
            )
            self.db.add(record)

        self.db.commit()

        return {
            "batch_id": batch_id,
            "total_generated": len(all_candidates),
            "valid": len(valid_candidates),
            "rejected": len(all_candidates) - len(valid_candidates),
            "final_top_n": min(final_top_n, len(valid_candidates)),
        }

    def ask_question(self, subject_id: int, question: str, top_k: int = 6) -> dict:
        try:
            results = self.rag_engine.retrieve(subject_id, question, top_k=top_k)
        except ValueError:
            raise ValueError("No knowledge base found for this subject — run build-knowledge-base first")

        context_chunks = [r["text"] for r in results]
        response = self.qa_engine.answer(question, context_chunks)

        sources = []
        for r in results:
            m = r["metadata"]
            if m.get("document_type") == "study_material":
                sources.append(f"{m.get('file_name', 'Study material')} (chunk {m.get('chunk_index')})")
            elif m.get("document_type") == "syllabus":
                sources.append(f"Syllabus: {m.get('file_name')}")
            elif m.get("document_type") == "previous_year_question":
                sources.append(f"PYQ {m.get('year')}: {m.get('topic', 'question')}")

        return {
            "answer": response.answer,
            "sources": list(dict.fromkeys(sources)),  # dedupe, preserve order
        }