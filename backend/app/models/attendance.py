"""Student attendance tracking model for the School Information Management System.

This module defines the Attendance model and related enums for recording daily
student presence, absences, and tardiness in the school system.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class AttendanceStatus(str, enum.Enum):
    """Enumeration of possible attendance statuses.
    
    Values:
        PRESENT: Student was present for the entire day/period.
        ABSENT: Student was absent without being marked late.
        LATE: Student arrived late but attended.
    """
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class Attendance(Base):
    """Represents a daily attendance record for a student.
    
    Attendance tracking is used to:
    - Monitor student presence and punctuality
    - Generate attendance reports for parents
    - Identify patterns of absenteeism
    - Meet regulatory reporting requirements
    - Trigger alerts for excessive absences
    
    Relationships:
        student: Many-to-one relationship with Student (multiple attendance records per student).
    
    Attributes:
        id (str): Unique identifier (UUID) for the attendance record.
        student_id (str): Foreign key linking to the student.
        date (date): Date for which attendance is being recorded.
        status (AttendanceStatus): Attendance status (present/absent/late).
        remarks (str): Optional notes about the attendance (e.g., "Medical leave", "Excused absence").
    """
    __tablename__ = "attendance"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"))
    date = Column(Date, nullable=False)  # Date of attendance record
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)  # Default to present
    remarks = Column(String, nullable=True)  # Optional notes (e.g., "Sick leave", "Family emergency")

    # Relationship for accessing student information
    student = relationship("Student", back_populates="attendance")
    