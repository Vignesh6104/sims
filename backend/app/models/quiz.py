from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    class_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False)
    
    # JSON field to store questions if we want to avoid complex mapping, 
    # but separate Question model is better for reporting.
    # Let's use a JSON field for the initial MVP of this feature for flexibility.
    # Format: [{"question": "...", "options": ["A", "B"], "correct_answer": 0, "points": 5}]
    questions_data = Column(JSON, nullable=False) 
    
    time_limit_minutes = Column(Integer, default=30)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    classroom = relationship("ClassRoom")
    subject = relationship("Subject")
    teacher = relationship("Teacher")

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    
    score = Column(Float, nullable=False)
    total_points = Column(Float, nullable=False)
    answers = Column(JSON, nullable=False) # Store student's chosen options
    
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    quiz = relationship("Quiz")
    student = relationship("Student")
