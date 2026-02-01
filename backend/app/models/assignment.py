import uuid
from sqlalchemy import Column, String, ForeignKey, Date, Text, Float
from sqlalchemy.orm import relationship
from app.db.session import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    class_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False)
    due_date = Column(Date, nullable=False)
    
    classroom = relationship("ClassRoom")
    subject = relationship("Subject")
    teacher = relationship("Teacher")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    submission_date = Column(Date, nullable=False)
    content = Column(Text, nullable=True) # Text submission or file URL
    grade = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)

    assignment = relationship("Assignment")
    student = relationship("Student")
