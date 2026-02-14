from sqlalchemy import Column, String, ForeignKey, Date, Enum, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.db.session import Base

class LeaveStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class LeaveType(str, enum.Enum):
    SICK = "SICK"
    CASUAL = "CASUAL"
    EMERGENCY = "EMERGENCY"
    OTHER = "OTHER"

class Leave(Base):
    __tablename__ = "leaves"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Using String for UUID foreign keys
    student_id = Column(String, ForeignKey("students.id"), nullable=True)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=True)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)
    leave_type = Column(Enum(LeaveType), default=LeaveType.OTHER)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student")
    teacher = relationship("Teacher")
