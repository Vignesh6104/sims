"""Student user model for the School Information Management System.

This module defines the Student model representing students enrolled in the school
who attend classes, submit assignments, and have their academic progress tracked.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Student(Base):
    """Represents a student in the school management system.
    
    Students are the primary beneficiaries of the education system, with access to:
    - View class schedules and timetables
    - Submit assignments
    - View marks and attendance records
    - Communicate with teachers
    - Access library resources
    
    Relationships:
        classroom: Many-to-one relationship with ClassRoom (student belongs to one class).
        parent: Many-to-one relationship with Parent (student linked to one parent account).
        attendance: One-to-many relationship with Attendance (tracks daily attendance).
        marks: One-to-many relationship with Mark (stores academic performance).
    
    Attributes:
        id (str): Unique identifier (UUID) for the student.
        email (str): Unique email address used for authentication.
        hashed_password (str): Securely hashed password for authentication.
        full_name (str): Full name of the student.
        is_active (bool): Enrollment status; False indicates withdrawn/inactive student.
        created_at (datetime): Timestamp when the student account was created.
        class_id (str): Foreign key linking to the student's assigned classroom.
        parent_id (str): Foreign key linking to the parent/guardian account.
        roll_number (str): Unique roll number for the student within their class/school.
        date_of_birth (date): Student's date of birth for age verification and records.
        address (str): Residential address of the student.
        profile_image (str): URL or path to the student's profile image.
    """
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)  # Indexed for fast login lookups
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)  # Used to track enrollment status
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    class_id = Column(String, ForeignKey("classrooms.id"), nullable=True)  # Links to assigned classroom
    parent_id = Column(String, ForeignKey("parents.id"), nullable=True)  # Links to parent/guardian
    roll_number = Column(String, index=True)  # Indexed for quick student lookup
    date_of_birth = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)  # Stores file path or URL

    # Relationships for navigating student's academic data
    classroom = relationship("ClassRoom", back_populates="students")
    parent = relationship("Parent", back_populates="students")
    attendance = relationship("Attendance", back_populates="student")
    marks = relationship("Mark", back_populates="student")