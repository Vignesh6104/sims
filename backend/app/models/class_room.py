"""Classroom/Class model for the School Information Management System.

This module defines the ClassRoom model representing physical or organizational
classes/sections where students are grouped and taught.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class ClassRoom(Base):
    """Represents a classroom or class section in the school.
    
    ClassRooms are organizational units that:
    - Group students together for instruction
    - Assign a primary class teacher
    - Define the scope for assignments and timetables
    - Organize fee structures and academic activities
    
    Relationships:
        teacher: Many-to-one relationship with Teacher (one teacher can manage multiple classes,
                 but each class has one primary teacher).
        students: One-to-many relationship with Student (multiple students per class).
    
    Attributes:
        id (str): Unique identifier (UUID) for the classroom.
        name (str): Name of the class (e.g., "Grade 10-A", "Class 5-B", "Year 12 Science").
                    Must be unique across the school.
        teacher_id (str): Foreign key linking to the assigned class teacher (optional).
    """
    __tablename__ = "classrooms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)  # Class name (e.g., "Grade 10-A", unique and indexed)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=True)  # Primary class teacher

    # Relationships for navigating class structure
    teacher = relationship("Teacher", back_populates="classrooms")  # Class teacher
    students = relationship("Student", back_populates="classroom")  # All students in this class