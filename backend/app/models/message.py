from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    sender_id = Column(String, nullable=False, index=True)
    sender_role = Column(String, nullable=False) # admin, teacher, student, parent
    sender_name = Column(String, nullable=True)
    
    receiver_id = Column(String, nullable=False, index=True)
    receiver_role = Column(String, nullable=False)
    receiver_name = Column(String, nullable=True)
    
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
