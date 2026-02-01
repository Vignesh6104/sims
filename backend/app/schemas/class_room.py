from pydantic import BaseModel
from typing import Optional, List
from app.schemas.student import Student

class ClassRoomBase(BaseModel):
    name: str

class ClassRoomCreate(ClassRoomBase):
    teacher_id: Optional[str] = None

class ClassRoomUpdate(ClassRoomBase):
    teacher_id: Optional[str] = None

class ClassRoomInDBBase(ClassRoomBase):
    id: str
    teacher_id: Optional[str] = None
    students: List[Student] = []

    class Config:
        from_attributes = True

class ClassRoom(ClassRoomInDBBase):
    pass