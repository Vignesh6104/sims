from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: str
    recipient_role: Optional[str] = None # 'all', 'teacher', 'student'
    recipient_id: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    is_read: bool

class NotificationInDBBase(NotificationBase):
    id: str
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True

class Notification(NotificationInDBBase):
    pass
