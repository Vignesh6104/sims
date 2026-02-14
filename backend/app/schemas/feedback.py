from typing import Optional
from datetime import datetime
from pydantic import BaseModel, UUID4
from app.models.feedback import FeedbackStatus, FeedbackPriority

# Shared properties
class FeedbackBase(BaseModel):
    subject: str
    description: str
    priority: Optional[FeedbackPriority] = FeedbackPriority.MEDIUM

# Properties to receive on creation
class FeedbackCreate(FeedbackBase):
    pass

# Properties to receive on update (Admin adding response/changing status)
class FeedbackUpdate(BaseModel):
    status: Optional[FeedbackStatus] = None
    admin_response: Optional[str] = None
    priority: Optional[FeedbackPriority] = None

# Properties shared by models stored in DB
class FeedbackInDBBase(FeedbackBase):
    id: UUID4
    status: FeedbackStatus
    admin_response: Optional[str] = None
    student_id: Optional[UUID4] = None
    teacher_id: Optional[UUID4] = None
    parent_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class Feedback(FeedbackInDBBase):
    pass
