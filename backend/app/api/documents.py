import os
import shutil
from enum import Enum
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.document import Document
from app.models.subject import Subject
from app.schemas.document import DocumentOut
from app.core.config import settings
from app.engine.document_processor import DocumentProcessor
from fastapi import HTTPException

router = APIRouter(prefix="/subjects", tags=["documents"])


class DocumentType(str, Enum):
    syllabus = "syllabus"
    study_material = "study_material"
    previous_year_question = "previous_year_question"


@router.post("/{subject_id}/documents", response_model=DocumentOut)
def upload_document(
    subject_id: int,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    folder = os.path.join(settings.upload_dir, f"subject_{subject_id}", document_type.value)
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        subject_id=subject_id,
        document_type=document_type.value,
        file_name=file.filename,
        file_path=file_path,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/{subject_id}/documents", response_model=list[DocumentOut])
def list_documents(subject_id: int, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.subject_id == subject_id).all()


@router.get("/{subject_id}/documents/{document_id}/preview")
def preview_document_text(subject_id: int, document_id: int, db: Session = Depends(get_db)):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.subject_id == subject_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    processor = DocumentProcessor()
    result = processor.process(document.file_path)

    return {
        "file_name": document.file_name,
        "raw_length": result["raw_length"],
        "cleaned_length": result["cleaned_length"],
        "num_chunks": result["num_chunks"],
        "first_500_chars": result["cleaned_text"][:500],
        "first_chunk": result["chunks"][0] if result["chunks"] else None,
    }
    
@router.delete("/{subject_id}/documents/{document_id}")
def delete_document(subject_id: int, document_id: int, db: Session = Depends(get_db)):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.subject_id == subject_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete the file from disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

    return {"message": f"Document '{document.file_name}' deleted successfully"}