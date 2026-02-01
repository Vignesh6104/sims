from pydantic import BaseModel
from typing import Optional
from datetime import date

class ExamBase(BaseModel):
    name: str
    date: date

class ExamCreate(ExamBase):
    pass

class ExamUpdate(ExamBase):
    pass

class ExamInDBBase(ExamBase):
    id: str

    class Config:
        from_attributes = True

class Exam(ExamInDBBase):
    pass