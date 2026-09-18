from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    question_text = Column(String, nullable=False)
    topic_id = Column(Integer, nullable=True)
    topic_name = Column(String, nullable=True)
    marks = Column(Integer, nullable=True)
    difficulty = Column(String, nullable=True)
    question_type = Column(String, nullable=True)
    evidence_score = Column(Float, nullable=True)
    evidence_breakdown = Column(String, nullable=True)   # JSON string — new
    generation_reason = Column(String, nullable=True)
    supporting_years = Column(String, nullable=True)
    status = Column(String, nullable=False, default="candidate")
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())