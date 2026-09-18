from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.analysis_service import AnalysisService
from app.models.syllabus import SyllabusUnit, SyllabusTopic, SyllabusSubtopic
from app.models.question import ExtractedQuestion
from app.models.concept import Concept
import json
from app.models.pattern import TopicPatternRecord
from app.models.generated_question import GeneratedQuestion
from fastapi.responses import Response
from app.engine.pdf_exporter import build_questions_pdf
from app.models.subject import Subject
from app.schemas.question import AskQuestionRequest


router = APIRouter(prefix="/subjects", tags=["analysis"])


@router.post("/{subject_id}/analyze-syllabus")
def analyze_syllabus(subject_id: int, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.analyze_syllabus(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/syllabus")
def get_syllabus(subject_id: int, db: Session = Depends(get_db)):
    units = db.query(SyllabusUnit).filter(SyllabusUnit.subject_id == subject_id).order_by(SyllabusUnit.unit_number).all()
    output = []
    for unit in units:
        topics = db.query(SyllabusTopic).filter(SyllabusTopic.unit_id == unit.id).all()
        topic_list = []
        for topic in topics:
            subtopics = db.query(SyllabusSubtopic).filter(SyllabusSubtopic.topic_id == topic.id).all()
            topic_list.append({
                "name": topic.topic_name,
                "subtopics": [s.subtopic_name for s in subtopics],
            })
        output.append({
            "unit_number": unit.unit_number,
            "unit_name": unit.unit_name,
            "topics": topic_list,
        })
    return {"units": output}


@router.post("/{subject_id}/extract-pyqs")
def extract_pyqs(subject_id: int, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.extract_pyqs(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/extracted-questions")
def get_extracted_questions(subject_id: int, db: Session = Depends(get_db)):
    questions = (
        db.query(ExtractedQuestion)
        .filter(ExtractedQuestion.subject_id == subject_id)
        .order_by(ExtractedQuestion.year, ExtractedQuestion.question_number)
        .all()
    )
    return [
        {
            "id": q.id,
            "year": q.year,
            "question_number": q.question_number,
            "question_text": q.question_text,
            "marks": q.marks,
            "question_type": q.question_type,
        }
        for q in questions
    ]
    

@router.post("/{subject_id}/classify-topics")
def classify_topics(subject_id: int, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.classify_topics(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/questions-by-topic")
def get_questions_by_topic(subject_id: int, db: Session = Depends(get_db)):
    from app.models.syllabus import SyllabusTopic, SyllabusUnit

    questions = db.query(ExtractedQuestion).filter(ExtractedQuestion.subject_id == subject_id).all()
    output = []
    for q in questions:
        topic_name = None
        unit_name = None
        if q.topic_id:
            topic = db.query(SyllabusTopic).filter(SyllabusTopic.id == q.topic_id).first()
            if topic:
                topic_name = topic.topic_name
                unit = db.query(SyllabusUnit).filter(SyllabusUnit.id == topic.unit_id).first()
                if unit:
                    unit_name = unit.unit_name
        output.append({
            "id": q.id,
            "year": q.year,
            "question_text": q.question_text,
            "topic_name": topic_name,
            "unit_name": unit_name,
        })
    return output


@router.post("/{subject_id}/map-concepts")
def map_concepts(subject_id: int, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.map_concepts(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/concepts")
def get_concepts(subject_id: int, db: Session = Depends(get_db)):
    concepts = db.query(Concept).filter(Concept.subject_id == subject_id).all()
    output = []
    for c in concepts:
        questions = db.query(ExtractedQuestion).filter(ExtractedQuestion.concept_id == c.id).all()
        output.append({
            "concept_id": c.id,
            "concept_name": c.concept_name,
            "num_questions": len(questions),
            "years": sorted(set(q.year for q in questions if q.year)),
            "question_ids": [q.id for q in questions],
        })
    return sorted(output, key=lambda x: -x["num_questions"])


@router.post("/{subject_id}/analyze-repetition")
def analyze_repetition(subject_id: int, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.analyze_repetition(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/repeated-questions")
def get_repeated_questions(subject_id: int, db: Session = Depends(get_db)):
    questions = (
        db.query(ExtractedQuestion)
        .filter(ExtractedQuestion.subject_id == subject_id, ExtractedQuestion.repetition_type.isnot(None))
        .order_by(ExtractedQuestion.repetition_group_id)
        .all()
    )
    return [
        {
            "id": q.id,
            "year": q.year,
            "question_text": q.question_text,
            "repetition_type": q.repetition_type,
            "repetition_group_id": q.repetition_group_id,
        }
        for q in questions
    ]
    
@router.post("/{subject_id}/analyze-patterns")
def analyze_patterns(subject_id: int, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.analyze_patterns(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/patterns")
def get_patterns(subject_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(TopicPatternRecord)
        .filter(TopicPatternRecord.subject_id == subject_id)
        .order_by(TopicPatternRecord.frequency.desc())
        .all()
    )
    return [
        {
            "topic_id": r.topic_id,
            "topic_name": r.topic_name,
            "unit_name": r.unit_name,
            "frequency": r.frequency,
            "total_papers": r.total_papers,
            "years": json.loads(r.years_json),
            "marks_distribution": json.loads(r.marks_distribution_json),
            "question_types": json.loads(r.question_types_json),
            "recurrence_intervals": json.loads(r.recurrence_intervals_json),
            "concept_count": r.concept_count,
            "exact_repeat_count": r.exact_repeat_count,
            "near_repeat_count": r.near_repeat_count,
        }
        for r in records
    ]
    
@router.post("/{subject_id}/build-knowledge-base")
def build_knowledge_base(subject_id: int, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.build_knowledge_base(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/knowledge-base-test")
def test_knowledge_base(subject_id: int, query: str, top_k: int = 5, db: Session = Depends(get_db)):
    """Quick manual test of retrieval — full RAG retrieval logic comes in Step 13."""
    service = AnalysisService(db)
    try:
        results = service.rag_engine.retrieve(subject_id, query, top_k)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return results

import os as _os

@router.get("/{subject_id}/knowledge-base-status")
def knowledge_base_status(subject_id: int, db: Session = Depends(get_db)):
    index_path = f"./storage/vectorstore/subject_{subject_id}/index.faiss"
    exists = _os.path.exists(index_path)
    return {"exists": exists}

@router.get("/{subject_id}/retrieve-for-topic")
def retrieve_for_topic(subject_id: int, topic: str, top_k: int = 5, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.rag_engine.retrieve_for_topic(subject_id, topic, top_k)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/blueprints")
def get_blueprints(subject_id: int, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.build_blueprints(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.post("/{subject_id}/generate-questions")
def generate_questions(subject_id: int, num_topics: int = 8, questions_per_topic: int = 4, final_top_n: int = 20, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.generate_questions(subject_id, num_topics, questions_per_topic, final_top_n)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/{subject_id}/final-questions")
def get_final_questions(subject_id: int, db: Session = Depends(get_db)):
    questions = (
        db.query(GeneratedQuestion)
        .filter(GeneratedQuestion.subject_id == subject_id, GeneratedQuestion.status == "ranked")
        .order_by(GeneratedQuestion.evidence_score.desc())
        .all()
    )
    return [
        {
            "id": q.id,
            "question_text": q.question_text,
            "topic_name": q.topic_name,
            "marks": q.marks,
            "difficulty": q.difficulty,
            "question_type": q.question_type,
            "evidence_score": q.evidence_score,
            "evidence_breakdown": json.loads(q.evidence_breakdown) if q.evidence_breakdown else None,
            "generation_reason": q.generation_reason,
            "supporting_years": json.loads(q.supporting_years) if q.supporting_years else [],
        }
        for q in questions
    ]


@router.get("/{subject_id}/all-candidates")
def get_all_candidates(subject_id: int, db: Session = Depends(get_db)):
    """Debug view: see rejected candidates too, not just the final ranked ones."""
    questions = db.query(GeneratedQuestion).filter(GeneratedQuestion.subject_id == subject_id).all()
    return [
        {
            "id": q.id,
            "question_text": q.question_text,
            "topic_name": q.topic_name,
            "status": q.status,
            "evidence_score": q.evidence_score,
            "rejection_reason": q.rejection_reason,
        }
        for q in questions
    ]
    

@router.get("/{subject_id}/final-questions/pdf")
def download_final_questions_pdf(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    questions = (
        db.query(GeneratedQuestion)
        .filter(GeneratedQuestion.subject_id == subject_id, GeneratedQuestion.status == "ranked")
        .order_by(GeneratedQuestion.evidence_score.desc())
        .all()
    )
    if not questions:
        raise HTTPException(status_code=404, detail="No final questions found — run generate-questions first")

    question_dicts = [
        {
            "question_text": q.question_text,
            "topic_name": q.topic_name,
            "marks": q.marks,
            "question_type": q.question_type,
            "evidence_score": q.evidence_score,
            "generation_reason": q.generation_reason,
        }
        for q in questions
    ]

    try:
        pdf_bytes = build_questions_pdf(subject.name, question_dicts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{subject.name}_question_bank.pdf"'},
    )
    
@router.post("/{subject_id}/ask")
def ask_question(subject_id: int, payload: AskQuestionRequest, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    try:
        result = service.ask_question(subject_id, payload.question)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result