from sqlalchemy import Column, String, ForeignKey, Text, Enum, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.db.session import Base

class FeedbackStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class FeedbackPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Using String for UUID foreign keys
    student_id = Column(String, ForeignKey("students.id"), nullable=True)
    parent_id = Column(String, ForeignKey("parents.id"), nullable=True)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=True)
    
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Enum(FeedbackPriority), default=FeedbackPriority.MEDIUM)
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.OPEN)
    
    admin_response = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student")
    parent = relationship("Parent")
    teacher = relationship("Teacher")
