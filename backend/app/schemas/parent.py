from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.schemas.student import Student

class ParentBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    is_active: bool = True

class ParentCreate(ParentBase):
    password: str

class ParentUpdate(ParentBase):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class ParentInDBBase(ParentBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Parent(ParentInDBBase):
    students: List[Student] = []
