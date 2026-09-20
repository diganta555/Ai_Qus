from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.connection import Base

class PipelineJob(Base):
    __tablename__ = "pipeline_jobs"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    step = Column(String, nullable=False)
    status = Column(String, nullable=False, default="running")
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())