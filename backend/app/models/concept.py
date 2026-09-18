from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connection import Base


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    concept_name = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey("syllabus_topics.id"), nullable=True)
    description = Column(String, nullable=True)