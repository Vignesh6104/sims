"""Notification model for the School Information Management System.

This module defines the Notification model for broadcasting announcements and
sending targeted notifications to users in the school system.

Note: Current implementation supports:
- Direct notifications to specific users (recipient_id set)
- Broadcast notifications to user roles (recipient_role set, recipient_id null)
For tracking read status of broadcasts, consider implementing a separate
NotificationRead mapping table in future versions.
"""
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Notification(Base):
    """Represents a system notification or announcement.
    
    Notifications are used to:
    - Broadcast school-wide announcements
    - Send targeted messages to specific user roles
    - Notify individual users about important updates
    - Communicate time-sensitive information
    
    Implementation notes:
    - For direct notifications: Set recipient_id to target a specific user
    - For broadcasts: Set recipient_role (e.g., "all", "teacher", "student") with recipient_id=null
    - Read status tracking works reliably only for direct notifications (recipient_id set)
    - For broadcasts, is_read field has limited utility; consider local client-side dismissal
    
    Attributes:
        id (str): Unique identifier (UUID) for the notification.
        title (str): Notification title/subject.
        message (str): Full notification message content.
        created_at (datetime): Timestamp when notification was created.
        recipient_role (str): Target role for broadcast ("all", "teacher", "student", "parent", "admin").
        recipient_id (str): Specific user ID for direct notifications (null for broadcasts).
        is_read (bool): Read status - reliable for direct notifications, limited use for broadcasts.
    """
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Targeting: Use recipient_role for broadcasts, recipient_id for direct messages
    recipient_role = Column(String, nullable=True)  # "all", "teacher", "student", "parent", or None for direct
    recipient_id = Column(String, nullable=True)  # Specific user ID for targeted notification
    
    # Read status: Works for direct messages; for broadcasts, tracking per-user read status requires additional table
    is_read = Column(Boolean, default=False)
