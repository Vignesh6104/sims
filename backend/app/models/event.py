import uuid
from sqlalchemy import Column, String, DateTime, Enum
from app.db.session import Base
import enum

class EventType(str, enum.Enum):
    HOLIDAY = "holiday"
    EXAM = "exam"
    EVENT = "event"

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    type = Column(String, default=EventType.EVENT)
