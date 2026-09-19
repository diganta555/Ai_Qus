from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class ExtractedQuestion(Base):
    __tablename__ = "extracted_questions"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    year = Column(Integer, nullable=True)
    question_number = Column(Integer, nullable=True)
    question_text = Column(String, nullable=False)
    marks = Column(Integer, nullable=True)
    question_type = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    topic_id = Column(Integer, nullable=True)
    subtopic_id = Column(Integer, nullable=True)
    concept_id = Column(Integer, nullable=True)
    repetition_type = Column(String, nullable=True)
    repetition_group_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
