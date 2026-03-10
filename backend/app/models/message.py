"""Direct messaging model for the School Information Management System.

This module defines the Message model for peer-to-peer communication between
users in the school system (teachers, students, parents, and admins).
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

class Message(Base):
    """Represents a direct message between two users in the system.
    
    Messages enable:
    - Direct communication between teachers and students
    - Parent-teacher communication
    - Student-to-student messaging
    - Admin announcements to individuals
    
    Implementation notes:
    - This is a simple peer-to-peer messaging system
    - Messages are one-directional (sender -> receiver)
    - Both sender and receiver IDs are generic strings that can reference any user type
    - Role fields track the type of user for proper routing and permissions
    - sender_name and receiver_name are denormalized for performance
    
    Attributes:
        id (str): Unique identifier (UUID) for the message.
        sender_id (str): User ID of the message sender (indexed for querying sent messages).
        sender_role (str): Role of sender ("admin", "teacher", "student", "parent").
        sender_name (str): Full name of sender (denormalized for quick display).
        receiver_id (str): User ID of the message recipient (indexed for querying inbox).
        receiver_role (str): Role of receiver ("admin", "teacher", "student", "parent").
        receiver_name (str): Full name of receiver (denormalized for quick display).
        content (str): Message content/body.
        is_read (bool): Whether the recipient has read the message.
        created_at (datetime): Timestamp when message was sent.
    """
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Sender information
    sender_id = Column(String, nullable=False, index=True)  # Indexed for "sent messages" queries
    sender_role = Column(String, nullable=False)  # "admin", "teacher", "student", "parent"
    sender_name = Column(String, nullable=True)  # Denormalized for display
    
    # Receiver information
    receiver_id = Column(String, nullable=False, index=True)  # Indexed for "inbox" queries
    receiver_role = Column(String, nullable=False)  # "admin", "teacher", "student", "parent"
    receiver_name = Column(String, nullable=True)  # Denormalized for display
    
    content = Column(Text, nullable=False)  # Message body
    is_read = Column(Boolean, default=False)  # Read status
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
