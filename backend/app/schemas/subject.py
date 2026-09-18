from pydantic import BaseModel
from datetime import datetime

class SubjectCreate(BaseModel):
    name: str

class SubjectOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True