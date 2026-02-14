from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, UUID4
from app.models.leave import LeaveStatus, LeaveType

# Shared properties
class LeaveBase(BaseModel):
    start_date: date
    end_date: date
    leave_type: LeaveType
    reason: str

# Properties to receive on creation
class LeaveCreate(LeaveBase):
    pass

# Properties to receive on update (only Admin/Teacher can update status/rejection)
class LeaveUpdate(BaseModel):
    status: Optional[LeaveStatus] = None
    rejection_reason: Optional[str] = None

# Properties shared by models stored in DB
class LeaveInDBBase(LeaveBase):
    id: UUID4 # Expecting UUID string
    status: LeaveStatus
    rejection_reason: Optional[str] = None
    student_id: Optional[UUID4] = None
    teacher_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class Leave(LeaveInDBBase):
    pass
