"""Feedback and issue tracking model for the School Information Management System.

This module defines the Feedback model and related enums for collecting and
managing feedback, suggestions, and issues from students, parents, and teachers.
"""
from sqlalchemy import Column, String, ForeignKey, Text, Enum, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.db.session import Base

class FeedbackStatus(str, enum.Enum):
    """Enumeration of possible feedback statuses in the resolution workflow.
    
    Values:
        OPEN: Feedback submitted, not yet being addressed.
        IN_PROGRESS: Feedback is being reviewed/addressed.
        RESOLVED: Issue has been resolved or feedback has been acted upon.
        CLOSED: Feedback has been closed (may or may not be resolved).
    """
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class FeedbackPriority(str, enum.Enum):
    """Enumeration of feedback priority levels.
    
    Values:
        LOW: Minor suggestions or non-urgent feedback.
        MEDIUM: Standard priority feedback (default).
        HIGH: Urgent issues requiring immediate attention.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Feedback(Base):
    """Represents feedback, suggestions, or issues submitted by users.
    
    Feedback system is used to:
    - Collect user suggestions for improvements
    - Report issues and problems
    - Track resolution of reported issues
    - Facilitate communication with administration
    - Improve school operations based on stakeholder input
    
    Business rules:
    - One of student_id, parent_id, or teacher_id must be set to identify the submitter
    - Admin can respond via admin_response field
    - Priority helps triage issues
    - Status tracks resolution workflow
    
    Relationships:
        student: Many-to-one relationship with Student (optional - submitter if student).
        parent: Many-to-one relationship with Parent (optional - submitter if parent).
        teacher: Many-to-one relationship with Teacher (optional - submitter if teacher).
    
    Attributes:
        id (str): Unique identifier (UUID) for the feedback.
        student_id (str): Foreign key linking to student submitter (null if not a student).
        parent_id (str): Foreign key linking to parent submitter (null if not a parent).
        teacher_id (str): Foreign key linking to teacher submitter (null if not a teacher).
        subject (str): Brief subject/title of the feedback.
        description (str): Detailed description of the feedback or issue.
        priority (FeedbackPriority): Urgency level (default: MEDIUM).
        status (FeedbackStatus): Current status in resolution workflow (default: OPEN).
        admin_response (str): Administrator's response or resolution notes (null until addressed).
        created_at (datetime): Timestamp when feedback was submitted.
        updated_at (datetime): Timestamp when feedback was last updated.
    """
    __tablename__ = "feedbacks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Submitter: One of student, parent, or teacher
    student_id = Column(String, ForeignKey("students.id"), nullable=True)
    parent_id = Column(String, ForeignKey("parents.id"), nullable=True)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=True)
    
    subject = Column(String, nullable=False)  # Feedback subject/title
    description = Column(Text, nullable=False)  # Detailed feedback content
    priority = Column(Enum(FeedbackPriority), default=FeedbackPriority.MEDIUM)  # Urgency level
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.OPEN)  # Resolution status
    
    admin_response = Column(Text, nullable=True)  # Admin's reply or resolution notes
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships for accessing submitter information
    student = relationship("Student")
    parent = relationship("Parent")
    teacher = relationship("Teacher")
