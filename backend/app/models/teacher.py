import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    qualification = Column(String, nullable=True)
    subject_specialization = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)

    classrooms = relationship("ClassRoom", back_populates="teacher")
