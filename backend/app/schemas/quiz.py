from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, UUID4

class QuestionSchema(BaseModel):
    question: str
    options: List[str]
    correct_answer: int # Index of the options list
    points: float = 1.0

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    class_id: UUID4
    subject_id: UUID4
    time_limit_minutes: int = 30
    is_published: bool = False

class QuizCreate(QuizBase):
    questions_data: List[QuestionSchema]

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None
    questions_data: Optional[List[QuestionSchema]] = None

class QuizInDB(QuizBase):
    id: UUID4
    teacher_id: UUID4
    questions_data: List[QuestionSchema]
    created_at: datetime

    class Config:
        from_attributes = True

class QuizResultCreate(BaseModel):
    quiz_id: UUID4
    answers: List[int] # Indices of student choices

class QuizResultInDB(BaseModel):
    id: UUID4
    quiz_id: UUID4
    student_id: UUID4
    score: float
    total_points: float
    completed_at: datetime

    class Config:
        from_attributes = True
