from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class StudentBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    roll_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    class_id: Optional[str] = None
    parent_id: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: Optional[bool] = True

class StudentCreate(StudentBase):
    password: str

class StudentUpdate(StudentBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile_image: Optional[str] = None

class StudentInDBBase(StudentBase):
    id: str

    class Config:
        from_attributes = True

class Student(StudentInDBBase):
    pass