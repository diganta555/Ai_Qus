from pydantic import BaseModel


class SubtopicSchema(BaseModel):
    name: str


class TopicSchema(BaseModel):
    name: str
    subtopics: list[str] = []


class UnitSchema(BaseModel):
    unit_number: int
    unit_name: str
    topics: list[TopicSchema]


class SyllabusStructure(BaseModel):
    units: list[UnitSchema]


class SyllabusOut(BaseModel):
    units: list[UnitSchema]