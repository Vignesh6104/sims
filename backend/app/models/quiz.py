"""Quiz and quiz result models for the School Information Management System.

This module defines the Quiz and QuizResult models for creating online quizzes
and tracking student performance on automated assessments.

Note: Quiz questions are stored as JSON data for flexibility. For more complex
quiz systems, consider creating separate Question and Answer models.
"""
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

class Quiz(Base):
    """Represents an online quiz or automated assessment.
    
    Quizzes are used to:
    - Create automated assessments with multiple-choice questions
    - Set time limits for completion
    - Provide instant feedback to students
    - Track student understanding of topics
    
    The questions_data field stores quiz questions in JSON format:
    [
        {
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": 1,  # Index of correct option (0-based)
            "points": 5
        },
        ...
    ]
    
    Relationships:
        classroom: Many-to-one relationship with ClassRoom (quiz is for a specific class).
        subject: Many-to-one relationship with Subject (quiz is for a specific subject).
        teacher: Many-to-one relationship with Teacher (teacher who created the quiz).
    
    Attributes:
        id (str): Unique identifier (UUID) for the quiz.
        title (str): Title/name of the quiz.
        description (str): Optional description or instructions for the quiz.
        class_id (str): Foreign key linking to the class this quiz is for.
        subject_id (str): Foreign key linking to the subject/course.
        teacher_id (str): Foreign key linking to the teacher who created the quiz.
        questions_data (JSON): Array of question objects with options and correct answers.
        time_limit_minutes (int): Time limit for completing the quiz (default: 30 minutes).
        is_published (bool): Whether the quiz is visible to students (default: False).
        created_at (datetime): Timestamp when the quiz was created.
    """
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    class_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False)
    
    # JSON field stores questions with options and correct answers
    # Format: [{"question": "...", "options": ["A", "B"], "correct_answer": 0, "points": 5}]
    questions_data = Column(JSON, nullable=False)
    
    time_limit_minutes = Column(Integer, default=30)  # Quiz time limit
    is_published = Column(Boolean, default=False)  # Controls visibility to students
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships for accessing quiz context
    classroom = relationship("ClassRoom")
    subject = relationship("Subject")
    teacher = relationship("Teacher")

class QuizResult(Base):
    """Represents a student's result for a completed quiz.
    
    QuizResults track:
    - Student performance on quizzes
    - Answers selected by students
    - Scores and completion times
    - Quiz attempt history
    
    The answers field stores student's selected options in JSON format:
    [0, 2, 1, 3, ...]  # Indices of selected options for each question
    
    Relationships:
        quiz: Many-to-one relationship with Quiz (result is for a specific quiz).
        student: Many-to-one relationship with Student (result belongs to a specific student).
    
    Attributes:
        id (str): Unique identifier (UUID) for the quiz result.
        quiz_id (str): Foreign key linking to the quiz that was taken.
        student_id (str): Foreign key linking to the student who took the quiz.
        score (float): Points scored by the student.
        total_points (float): Maximum points possible for the quiz.
        answers (JSON): Array of student's selected answer indices.
        completed_at (datetime): Timestamp when the quiz was completed.
    """
    __tablename__ = "quiz_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    
    score = Column(Float, nullable=False)  # Points scored
    total_points = Column(Float, nullable=False)  # Maximum possible points
    answers = Column(JSON, nullable=False)  # Student's selected answer indices
    
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships for accessing result context
    quiz = relationship("Quiz")
    student = relationship("Student")
