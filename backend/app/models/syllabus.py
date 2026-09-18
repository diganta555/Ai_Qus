from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connection import Base


class SyllabusUnit(Base):
    __tablename__ = "syllabus_units"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    unit_number = Column(Integer, nullable=False)
    unit_name = Column(String, nullable=False)


class SyllabusTopic(Base):
    __tablename__ = "syllabus_topics"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("syllabus_units.id"), nullable=False)
    topic_name = Column(String, nullable=False)


class SyllabusSubtopic(Base):
    __tablename__ = "syllabus_subtopics"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("syllabus_topics.id"), nullable=False)
    subtopic_name = Column(String, nullable=False)