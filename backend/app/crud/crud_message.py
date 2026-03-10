"""CRUD operations for direct messaging between users.

This module handles one-to-one messaging functionality with conversation
threading and message history retrieval. Supports communication between
all user types (students, teachers, parents, admins).
"""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.message import Message
from app.schemas.message import MessageCreate


def create_message(db: Session, message: MessageCreate, sender_id: str, sender_role: str, sender_name: str):
    """Create and send a new message.
    
    Args:
        db: Database session for query execution.
        message: MessageCreate schema with receiver and content.
        sender_id: Unique identifier of the sender.
        sender_role: Role of the sender (student, teacher, parent, admin).
        sender_name: Full name of the sender for display.
        
    Returns:
        Newly created Message object with generated ID and timestamp.
        
    Note:
        Stores both sender and receiver metadata for efficient querying.
    """
    db_message = Message(
        sender_id=sender_id,
        sender_role=sender_role,
        sender_name=sender_name,
        receiver_id=message.receiver_id,
        receiver_role=message.receiver_role,
        receiver_name=message.receiver_name,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_conversation(db: Session, user_a_id: str, user_b_id: str, limit: int = 50):
    """Retrieve conversation history between two users.
    
    Fetches all messages exchanged between two users in chronological order.
    
    Args:
        db: Database session for query execution.
        user_a_id: Unique identifier of first user.
        user_b_id: Unique identifier of second user.
        limit: Maximum number of messages to return (default: 50).
        
    Returns:
        List of Message objects in chronological order (oldest first).
        
    Note:
        Bidirectional query: Messages where A->B OR B->A.
        Uses SQL AND/OR combination for efficient filtering.
    """
    # Bidirectional conversation query
    return db.query(Message).filter(
        or_(
            and_(Message.sender_id == user_a_id, Message.receiver_id == user_b_id),
            and_(Message.sender_id == user_b_id, Message.receiver_id == user_a_id)
        )
    ).order_by(Message.created_at.asc()).limit(limit).all()


def get_user_messages(db: Session, user_id: str, limit: int = 100):
    """Retrieve all messages involving a specific user.
    
    Includes both sent and received messages for inbox view.
    
    Args:
        db: Database session for query execution.
        user_id: Unique identifier of the user.
        limit: Maximum number of messages to return (default: 100).
        
    Returns:
        List of Message objects, ordered newest first.
        
    Note:
        Fetches messages where user is sender OR receiver.
    """
    return db.query(Message).filter(
        or_(Message.sender_id == user_id, Message.receiver_id == user_id)
    ).order_by(Message.created_at.desc()).limit(limit).all()
