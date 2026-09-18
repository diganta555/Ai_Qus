from pydantic import BaseModel
from datetime import datetime

class DocumentOut(BaseModel):
    id: int
    subject_id: int
    document_type: str
    file_name: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True