"""Assignment and submission models for the School Information Management System.

This module defines the Assignment and Submission models for managing homework,
projects, and other tasks assigned to students by teachers.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Date, Text, Float
from sqlalchemy.orm import relationship
from app.db.session import Base

class Assignment(Base):
    """Represents a homework assignment or project given to a class.
    
    Assignments are used to:
    - Assign tasks to students for completion outside class
    - Set deadlines for submission
    - Track pending work and submissions
    - Provide learning resources and instructions
    
    Relationships:
        classroom: Many-to-one relationship with ClassRoom (assignment is for a specific class).
        subject: Many-to-one relationship with Subject (assignment is for a specific subject).
        teacher: Many-to-one relationship with Teacher (teacher who created the assignment).
    
    Attributes:
        id (str): Unique identifier (UUID) for the assignment.
        title (str): Title/name of the assignment (e.g., "Chapter 5 Exercises").
        description (str): Detailed instructions and requirements for the assignment.
        class_id (str): Foreign key linking to the class this assignment is for.
        subject_id (str): Foreign key linking to the subject/course.
        teacher_id (str): Foreign key linking to the teacher who created the assignment.
        due_date (date): Deadline for submission.
    """
    __tablename__ = "assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # Detailed assignment instructions
    class_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False)
    due_date = Column(Date, nullable=False)  # Submission deadline
    
    # Relationships for accessing assignment context
    classroom = relationship("ClassRoom")
    subject = relationship("Subject")
    teacher = relationship("Teacher")

class Submission(Base):
    """Represents a student's submission for an assignment.
    
    Submissions track:
    - Student work submitted for assignments
    - Submission dates (to identify late submissions)
    - Grading and teacher feedback
    - Student performance on assignments
    
    Relationships:
        assignment: Many-to-one relationship with Assignment (submission is for a specific assignment).
        student: Many-to-one relationship with Student (submission belongs to a specific student).
    
    Attributes:
        id (str): Unique identifier (UUID) for the submission.
        assignment_id (str): Foreign key linking to the assignment being submitted.
        student_id (str): Foreign key linking to the student who submitted.
        submission_date (date): Date when the submission was made.
        content (str): Text content of submission or URL/path to submitted file.
        grade (float): Marks/grade awarded by teacher (optional until graded).
        feedback (str): Teacher's feedback or comments on the submission.
    """
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    submission_date = Column(Date, nullable=False)  # Actual submission date
    content = Column(Text, nullable=True)  # Text submission content or file URL/path
    grade = Column(Float, nullable=True)  # Marks awarded (null until graded)
    feedback = Column(Text, nullable=True)  # Teacher's comments/feedback

    # Relationships for accessing submission context
    assignment = relationship("Assignment")
    student = relationship("Student")
