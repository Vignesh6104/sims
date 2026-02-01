from pydantic import BaseModel
from typing import Optional

class MarkBase(BaseModel):
    subject: str
    score: float
    max_score: Optional[float] = 100.0
    exam_id: Optional[str] = None

class MarkCreate(MarkBase):
    student_id: str
    exam_id: str

class MarkUpdate(MarkBase):
    pass

class MarkInDBBase(MarkBase):
    id: str
    student_id: str

    class Config:
        from_attributes = True

class Mark(MarkInDBBase):
    pass