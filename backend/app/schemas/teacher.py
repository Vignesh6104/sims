from pydantic import BaseModel, EmailStr
from typing import Optional

class TeacherBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    qualification: Optional[str] = None
    subject_specialization: Optional[str] = None
    is_active: Optional[bool] = True

class TeacherCreate(TeacherBase):
    password: str

class TeacherUpdate(TeacherBase):
    password: Optional[str] = None

class TeacherInDBBase(TeacherBase):
    id: str

    class Config:
        from_attributes = True

class Teacher(TeacherInDBBase):
    pass