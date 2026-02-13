from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.event import EventType

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    type: EventType = EventType.EVENT

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventInDBBase(EventBase):
    id: str

    class Config:
        from_attributes = True

class Event(EventInDBBase):
    pass