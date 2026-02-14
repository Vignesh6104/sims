from typing import Optional
from datetime import datetime
from pydantic import BaseModel, UUID4

class MessageBase(BaseModel):
    receiver_id: str
    receiver_role: str
    content: str

class MessageCreate(MessageBase):
    receiver_name: Optional[str] = None

class MessageUpdate(BaseModel):
    is_read: bool

class MessageInDB(MessageBase):
    id: UUID4
    sender_id: str
    sender_role: str
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Message(MessageInDB):
    pass
