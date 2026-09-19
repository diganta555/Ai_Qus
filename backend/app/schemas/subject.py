from pydantic import BaseModel
from datetime import datetime

class SubjectCreate(BaseModel):
    name: str
    subject_code: str | None = None
    description: str | None = None
    category: str | None = None

class SubjectOut(BaseModel):
    id: int
    name: str
    subject_code: str | None = None
    description: str | None = None
    category: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
