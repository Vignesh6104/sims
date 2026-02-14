import uuid
from sqlalchemy import Column, String, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    class_id = Column(String, ForeignKey("classrooms.id"), nullable=True)
    parent_id = Column(String, ForeignKey("parents.id"), nullable=True)
    roll_number = Column(String, index=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)

    classroom = relationship("ClassRoom", back_populates="students")
    parent = relationship("Parent", back_populates="students")
    attendance = relationship("Attendance", back_populates="student")
    marks = relationship("Mark", back_populates="student")