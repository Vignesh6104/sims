"""Leave application and tracking model for the School Information Management System.

This module defines the Leave model and related enums for managing leave requests
from students and teachers, including approval workflows.
"""
from sqlalchemy import Column, String, ForeignKey, Date, Enum, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.db.session import Base

class LeaveStatus(str, enum.Enum):
    """Enumeration of possible leave application statuses.
    
    Values:
        PENDING: Leave application submitted, awaiting review.
        APPROVED: Leave application has been approved.
        REJECTED: Leave application has been rejected.
    """
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class LeaveType(str, enum.Enum):
    """Enumeration of leave categories.
    
    Values:
        SICK: Medical/health-related leave.
        CASUAL: General casual leave.
        EMERGENCY: Emergency or urgent leave.
        OTHER: Other types of leave not covered above.
    """
    SICK = "SICK"
    CASUAL = "CASUAL"
    EMERGENCY = "EMERGENCY"
    OTHER = "OTHER"

class Leave(Base):
    """Represents a leave application from a student or teacher.
    
    Leave applications are used to:
    - Request time off from school
    - Track approved and pending absences
    - Maintain leave records for compliance
    - Manage approval workflows
    
    Business rules:
    - Either student_id OR teacher_id must be set (not both)
    - Status starts as PENDING and moves to APPROVED/REJECTED
    - rejection_reason is set only when status is REJECTED
    
    Relationships:
        student: Many-to-one relationship with Student (optional - applicant if student).
        teacher: Many-to-one relationship with Teacher (optional - applicant if teacher).
    
    Attributes:
        id (str): Unique identifier (UUID) for the leave application.
        student_id (str): Foreign key linking to student applicant (null if teacher applied).
        teacher_id (str): Foreign key linking to teacher applicant (null if student applied).
        start_date (date): First day of leave.
        end_date (date): Last day of leave (inclusive).
        reason (str): Applicant's reason for requesting leave.
        status (LeaveStatus): Current status of the application (default: PENDING).
        leave_type (LeaveType): Category of leave being requested (default: OTHER).
        rejection_reason (str): Explanation if leave was rejected (null otherwise).
        created_at (datetime): Timestamp when leave application was submitted.
        updated_at (datetime): Timestamp when leave status was last updated.
    """
    __tablename__ = "leaves"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Applicant: Either student or teacher (one must be set)
    student_id = Column(String, ForeignKey("students.id"), nullable=True)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=True)
    
    start_date = Column(Date, nullable=False)  # Leave start date
    end_date = Column(Date, nullable=False)  # Leave end date (inclusive)
    reason = Column(Text, nullable=False)  # Reason for leave
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)  # Approval status
    leave_type = Column(Enum(LeaveType), default=LeaveType.OTHER)  # Leave category
    rejection_reason = Column(Text, nullable=True)  # Set when leave is rejected
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships for accessing applicant information
    student = relationship("Student")
    teacher = relationship("Teacher")
