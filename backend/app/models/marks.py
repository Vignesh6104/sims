import uuid
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.session import Base

class Mark(Base):
    __tablename__ = "marks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"))
    subject = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    exam_id = Column(String, ForeignKey("exams.id"), nullable=True)

    student = relationship("Student", back_populates="marks")
    exam = relationship("Exam", back_populates="marks")