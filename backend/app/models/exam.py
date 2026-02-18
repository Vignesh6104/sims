"""Examination model for the School Information Management System.

This module defines the Exam model for managing formal examinations and tests
conducted in the school.
"""
import uuid
from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship
from app.db.session import Base

class Exam(Base):
    """Represents a formal examination or test in the school.
    
    Exams are used to:
    - Schedule formal assessments (mid-term, final exams, unit tests)
    - Group related marks together for reporting
    - Generate consolidated result sheets
    - Track examination dates and organization
    
    Relationships:
        marks: One-to-many relationship with Mark (one exam can have multiple subject marks).
    
    Attributes:
        id (str): Unique identifier (UUID) for the exam.
        name (str): Name/title of the exam (e.g., "Mid-Term 2024", "Final Examination").
        date (date): Scheduled date for the examination.
    """
    __tablename__ = "exams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # e.g., "Mid-Term Exam 2024", "Final Examination"
    date = Column(Date, nullable=False)  # Scheduled exam date
    
    # Relationship: One exam can have multiple marks across subjects and students
    marks = relationship("Mark", back_populates="exam")