"""Student marks/grades model for the School Information Management System.

This module defines the Mark model for recording and tracking student academic
performance in various subjects and examinations.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.session import Base

class Mark(Base):
    """Represents a student's score for a subject or examination.
    
    Marks are recorded to:
    - Track student performance over time
    - Generate report cards and transcripts
    - Calculate cumulative grades and GPA
    - Identify students needing additional support
    
    Relationships:
        student: Many-to-one relationship with Student (multiple marks per student).
        exam: Many-to-one relationship with Exam (optional - marks can be for general assessments).
    
    Attributes:
        id (str): Unique identifier (UUID) for the mark record.
        student_id (str): Foreign key linking to the student who received the mark.
        subject (str): Name of the subject for this mark (e.g., "Mathematics", "Science").
        score (float): Actual score/marks obtained by the student.
        max_score (float): Maximum possible score for this assessment (default: 100.0).
        exam_id (str): Optional foreign key linking to a specific exam/test.
    """
    __tablename__ = "marks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"))
    subject = Column(String, nullable=False)  # Subject name for this mark
    score = Column(Float, nullable=False)  # Actual marks obtained
    max_score = Column(Float, default=100.0)  # Maximum marks possible (for percentage calculation)
    exam_id = Column(String, ForeignKey("exams.id"), nullable=True)  # Optional link to specific exam

    # Relationships for accessing related student and exam data
    student = relationship("Student", back_populates="marks")
    exam = relationship("Exam", back_populates="marks")