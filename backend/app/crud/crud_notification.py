"""CRUD operations for notification management.

This module handles system-wide notifications and announcements with support
for role-based broadcasting and individual targeting. Includes read/unread tracking.
"""

from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


def create_notification(db: Session, notification: NotificationCreate):
    """Create a new notification.
    
    Args:
        db: Database session for query execution.
        notification: NotificationCreate schema with notification details.
        
    Returns:
        Newly created Notification object with generated ID.
        
    Note:
        Supports both individual (recipient_id) and broadcast (recipient_role).
    """
    db_notification = Notification(**notification.model_dump())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_notifications_for_user(db: Session, user_id: str, role: str, skip: int = 0, limit: int = 100):
    """Retrieve all notifications for a specific user with role-based filtering.
    
    Fetches notifications targeted directly to the user OR broadcast to their
    role OR broadcast to 'all' users. Results are ordered by creation time.
    
    Args:
        db: Database session for query execution.
        user_id: Unique identifier of the user.
        role: User's role (student, teacher, parent, admin).
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Notification objects for the user, ordered newest first.
        
    Note:
        Complex filtering: Direct messages OR role broadcasts OR 'all' broadcasts.
        Uses SQL OR conditions for efficient single-query retrieval.
    """
    # Fetch direct messages OR broadcasts to their role OR broadcasts to 'all'
    return db.query(Notification).filter(
        (Notification.recipient_id == user_id) | 
        (Notification.recipient_role == role) |
        (Notification.recipient_role == 'all')
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def mark_notification_read(db: Session, notification_id: str):
    """Mark a notification as read.
    
    Args:
        db: Database session for query execution.
        notification_id: Unique identifier of the notification.
        
    Returns:
        Updated Notification object if found, None otherwise.
    """
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if db_notification:
        db_notification.is_read = True
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
    return db_notification
