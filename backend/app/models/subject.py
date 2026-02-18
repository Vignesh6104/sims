"""Subject/Course model for the School Information Management System.

This module defines the Subject model representing academic subjects or courses
offered in the school curriculum.
"""
import uuid
from sqlalchemy import Column, String
from app.db.session import Base

class Subject(Base):
    """Represents an academic subject or course in the school curriculum.
    
    Subjects are used to:
    - Define the curriculum and course offerings
    - Link assignments and exams to specific subjects
    - Organize timetables and schedules
    - Track teacher specializations
    - Generate subject-wise reports
    
    Attributes:
        id (str): Unique identifier (UUID) for the subject.
        name (str): Name of the subject (e.g., "Mathematics", "Physics", "English Literature").
                    Must be unique across the system.
        code (str): Optional subject code for identification (e.g., "MATH101", "PHY201").
                    Must be unique if provided.
    """
    __tablename__ = "subjects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)  # Subject name (unique and indexed)
    code = Column(String, unique=True, index=True, nullable=True)  # Optional subject code (e.g., "MATH101")