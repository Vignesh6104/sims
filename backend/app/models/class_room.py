import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class ClassRoom(Base):
    __tablename__ = "classrooms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=True)

    teacher = relationship("Teacher", back_populates="classrooms")
    students = relationship("Student", back_populates="classroom")