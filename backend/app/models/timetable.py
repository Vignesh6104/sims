"""Class timetable/schedule model for the School Information Management System.

This module defines the Timetable model and related enums for managing weekly
class schedules, period assignments, and subject-teacher allocations.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class DayOfWeek(str, enum.Enum):
    """Enumeration of days of the week for timetable scheduling.
    
    Values represent the seven days of the week for creating weekly schedules.
    """
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class Timetable(Base):
    """Represents a single period in a class's weekly timetable.
    
    Timetable entries define:
    - What subject is taught in each period
    - Which teacher conducts the class
    - When the period occurs (day and time)
    - Period sequencing and scheduling
    
    The complete timetable for a class is built from multiple Timetable records,
    one for each period of each day.
    
    Relationships:
        classroom: Many-to-one relationship with ClassRoom (timetable entry is for a specific class).
        subject: Many-to-one relationship with Subject (the subject taught in this period).
        teacher: Many-to-one relationship with Teacher (the teacher conducting this period).
    
    Attributes:
        id (str): Unique identifier (UUID) for the timetable entry.
        class_id (str): Foreign key linking to the class this period belongs to.
        subject_id (str): Foreign key linking to the subject taught in this period.
        teacher_id (str): Foreign key linking to the teacher assigned to this period.
        day (DayOfWeek): Day of the week for this period.
        period (int): Period number (e.g., 1, 2, 3... for sequential periods in a day).
        start_time (str): Period start time in 24-hour format (e.g., "09:00").
        end_time (str): Period end time in 24-hour format (e.g., "10:00").
    """
    __tablename__ = "timetables"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False)
    day = Column(Enum(DayOfWeek), nullable=False)  # Day of week
    period = Column(Integer, nullable=False)  # Period number (e.g., 1st period, 2nd period)
    start_time = Column(String, nullable=True)  # Start time in "HH:MM" format (e.g., "09:00")
    end_time = Column(String, nullable=True)  # End time in "HH:MM" format (e.g., "10:00")

    # Relationships for accessing timetable context
    classroom = relationship("ClassRoom")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
