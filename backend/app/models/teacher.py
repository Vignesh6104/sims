"""Teacher user model for the School Information Management System.

This module defines the Teacher model representing teaching staff who manage
classrooms, conduct lessons, create assessments, and track student progress.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Teacher(Base):
    """Represents a teacher in the school management system.
    
    Teachers are responsible for:
    - Managing assigned classrooms
    - Creating and grading assignments and exams
    - Tracking student attendance
    - Recording student marks
    - Communicating with students and parents
    
    Relationships:
        classrooms: One-to-many relationship with ClassRoom (one teacher can manage multiple classes).
    
    Attributes:
        id (str): Unique identifier (UUID) for the teacher.
        email (str): Unique email address used for authentication.
        hashed_password (str): Securely hashed password for authentication.
        full_name (str): Full name of the teacher.
        is_active (bool): Account status; False indicates deactivated account.
        created_at (datetime): Timestamp when the teacher account was created.
        qualification (str): Educational qualifications (e.g., "M.Ed", "Ph.D in Physics").
        subject_specialization (str): Primary subject expertise (e.g., "Mathematics", "Science").
        profile_image (str): URL or path to the teacher's profile image.
    """
    __tablename__ = "teachers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)  # Indexed for fast login lookups
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)  # Used to disable accounts without deletion
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    qualification = Column(String, nullable=True)  # e.g., "M.Ed", "B.Sc", "Ph.D"
    subject_specialization = Column(String, nullable=True)  # Primary teaching subject
    profile_image = Column(String, nullable=True)  # Stores file path or URL

    # Relationship: One teacher can be assigned to multiple classrooms
    classrooms = relationship("ClassRoom", back_populates="teacher")
