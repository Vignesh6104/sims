from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.models.attendance import AttendanceStatus

class AttendanceBase(BaseModel):
    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    student_id: str

class AttendanceUpdate(AttendanceBase):
    pass

class AttendanceInDBBase(AttendanceBase):
    id: str
    student_id: str

    class Config:
        from_attributes = True

class Attendance(AttendanceInDBBase):
    pass