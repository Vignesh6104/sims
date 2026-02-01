import uuid
from sqlalchemy import Column, String, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"))
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    remarks = Column(String, nullable=True)

    student = relationship("Student", back_populates="attendance")