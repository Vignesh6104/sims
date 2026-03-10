"""Parent/Guardian user model for the School Information Management System.

This module defines the Parent model representing parents or guardians who monitor
their children's academic progress and communicate with teachers and school staff.

Note: Current implementation uses a simplified one-parent-per-student model.
In future versions, this could be extended to support multiple guardians per student
through a many-to-many relationship.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Parent(Base):
    """Represents a parent or guardian in the school management system.
    
    Parents have access to:
    - View their children's academic performance
    - Monitor attendance records
    - Communicate with teachers
    - Receive notifications about school events
    - Track fee payments
    
    Relationships:
        students: One-to-many relationship with Student (one parent can have multiple children).
                  Currently implemented as a simplified model where each student links to one parent.
    
    Attributes:
        id (str): Unique identifier (UUID) for the parent.
        email (str): Unique email address used for authentication.
        hashed_password (str): Securely hashed password for authentication.
        full_name (str): Full name of the parent/guardian.
        phone_number (str): Contact phone number for emergency communication.
        profile_image (str): URL or path to the parent's profile image.
        is_active (bool): Account status; False indicates deactivated account.
        created_at (datetime): Timestamp when the parent account was created.
    """
    __tablename__ = "parents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)  # Indexed for fast login lookups
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)  # For emergency contact and SMS notifications
    profile_image = Column(String, nullable=True)  # Stores file path or URL
    is_active = Column(Boolean, default=True)  # Used to disable accounts without deletion
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship: One parent can have multiple children (students)
    # Student model contains parent_id foreign key for the reverse link
    students = relationship("Student", back_populates="parent")
