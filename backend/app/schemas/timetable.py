from pydantic import BaseModel
from typing import Optional
from app.models.timetable import DayOfWeek

class TimetableBase(BaseModel):
    day: DayOfWeek
    period: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class TimetableCreate(TimetableBase):
    class_id: str
    subject_id: str
    teacher_id: str

class TimetableUpdate(TimetableBase):
    pass

class TimetableInDBBase(TimetableBase):
    id: str
    class_id: str
    subject_id: str
    teacher_id: str

    class Config:
        from_attributes = True

class Timetable(TimetableInDBBase):
    pass
