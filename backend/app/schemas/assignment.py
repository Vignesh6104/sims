from pydantic import BaseModel
from typing import Optional
from datetime import date

# Assignment Schemas
class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: date

class AssignmentCreate(AssignmentBase):
    class_id: str
    subject_id: str
    teacher_id: str

class AssignmentUpdate(AssignmentBase):
    pass

class AssignmentInDBBase(AssignmentBase):
    id: str
    class_id: str
    subject_id: str
    teacher_id: str

    class Config:
        from_attributes = True

class Assignment(AssignmentInDBBase):
    pass

# Submission Schemas
class SubmissionBase(BaseModel):
    content: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    assignment_id: str
    student_id: str
    submission_date: date = date.today()

class SubmissionUpdate(BaseModel):
    grade: Optional[float] = None
    feedback: Optional[str] = None

class SubmissionInDBBase(SubmissionBase):
    id: str
    assignment_id: str
    student_id: str
    submission_date: date
    grade: Optional[float] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

class Submission(SubmissionInDBBase):
    student_name: Optional[str] = None
