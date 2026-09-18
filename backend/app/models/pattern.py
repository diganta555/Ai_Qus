from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connection import Base


class TopicPatternRecord(Base):
    __tablename__ = "topic_patterns"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    topic_id = Column(Integer, nullable=False)
    topic_name = Column(String, nullable=False)
    unit_name = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)
    total_papers = Column(Integer, nullable=False)
    years_json = Column(String, nullable=False)              # store as JSON string
    marks_distribution_json = Column(String, nullable=False)
    question_types_json = Column(String, nullable=False)
    recurrence_intervals_json = Column(String, nullable=False)
    concept_count = Column(Integer, nullable=False)
    exact_repeat_count = Column(Integer, nullable=False)
    near_repeat_count = Column(Integer, nullable=False)