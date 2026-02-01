import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class DayOfWeek(str, enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class Timetable(Base):
    __tablename__ = "timetables"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False)
    day = Column(Enum(DayOfWeek), nullable=False)
    period = Column(Integer, nullable=False) # e.g., 1, 2, 3...
    start_time = Column(String, nullable=True) # "09:00"
    end_time = Column(String, nullable=True)   # "10:00"

    classroom = relationship("ClassRoom")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
