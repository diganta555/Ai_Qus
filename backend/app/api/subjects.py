import os
import shutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.subject import Subject
from app.models.document import Document
from app.models.question import ExtractedQuestion
from app.models.concept import Concept
from app.models.pattern import TopicPatternRecord
from app.models.generated_question import GeneratedQuestion
from app.models.syllabus import SyllabusUnit, SyllabusTopic, SyllabusSubtopic
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectOut
from app.core.config import settings
from app.core.auth import get_current_user

router = APIRouter(prefix="/subjects", tags=["subjects"])


def _get_owned_subject(subject_id: int, db: Session, current_user: User) -> Subject:
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subject.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this subject")
    return subject


@router.post("", response_model=SubjectOut)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subject = Subject(name=payload.name, user_id=current_user.id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Subject).filter(Subject.user_id == current_user.id).all()


@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_owned_subject(subject_id, db, current_user)


@router.delete("/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subject = _get_owned_subject(subject_id, db, current_user)

    db.query(GeneratedQuestion).filter(GeneratedQuestion.subject_id == subject_id).delete()
    db.query(TopicPatternRecord).filter(TopicPatternRecord.subject_id == subject_id).delete()
    db.query(Concept).filter(Concept.subject_id == subject_id).delete()
    db.query(ExtractedQuestion).filter(ExtractedQuestion.subject_id == subject_id).delete()

    units = db.query(SyllabusUnit).filter(SyllabusUnit.subject_id == subject_id).all()
    for unit in units:
        topics = db.query(SyllabusTopic).filter(SyllabusTopic.unit_id == unit.id).all()
        for topic in topics:
            db.query(SyllabusSubtopic).filter(SyllabusSubtopic.topic_id == topic.id).delete()
        db.query(SyllabusTopic).filter(SyllabusTopic.unit_id == unit.id).delete()
    db.query(SyllabusUnit).filter(SyllabusUnit.subject_id == subject_id).delete()

    db.query(Document).filter(Document.subject_id == subject_id).delete()
    db.commit()

    upload_folder = os.path.join(settings.upload_dir, f"subject_{subject_id}")
    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)

    vectorstore_folder = os.path.join("./storage/vectorstore", f"subject_{subject_id}")
    if os.path.exists(vectorstore_folder):
        shutil.rmtree(vectorstore_folder)

    db.delete(subject)
    db.commit()

    return {"message": f"Subject '{subject.name}' and all related data deleted successfully"}