import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Targeting
    recipient_role = Column(String, nullable=True) # "all", "teacher", "student", or specific ID
    recipient_id = Column(String, nullable=True) # If targeting specific user
    
    is_read = Column(Boolean, default=False) # Note: For broadcast messages, tracking read status per user requires a mapping table.
    # For MVP Phase 2, we will simplify: 
    # 1. Direct messages (recipient_id set) -> is_read works.
    # 2. Broadcasts -> is_read is ignored (always shown until dismissed locally or we create NotificationRead status table).
    # Let's stick to Direct Notifications + simple Broadcasts (stateless read) for now to keep schema simple.
    # Or better: "Announcements" table for broadcasts, "Notifications" for direct.
    # Let's use a single table. If recipient_id is NULL, it's a broadcast to 'recipient_role'.
