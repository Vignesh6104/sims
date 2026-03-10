"""Event and calendar model for the School Information Management System.

This module defines the Event model and related enums for managing the school
calendar, including holidays, examinations, and special events.
"""
import uuid
from sqlalchemy import Column, String, DateTime, Enum
from app.db.session import Base
import enum

class EventType(str, enum.Enum):
    """Enumeration of possible event types in the school calendar.
    
    Values:
        HOLIDAY: School holidays and vacation days.
        EXAM: Scheduled examinations and tests.
        EVENT: Special events (sports day, cultural programs, parent-teacher meetings, etc.).
    """
    HOLIDAY = "holiday"
    EXAM = "exam"
    EVENT = "event"

class Event(Base):
    """Represents a calendar event in the school system.
    
    Events are used to:
    - Display school calendar to all users
    - Schedule holidays and vacation periods
    - Mark examination dates
    - Announce special events and programs
    - Coordinate school-wide activities
    
    Attributes:
        id (str): Unique identifier (UUID) for the event.
        title (str): Event title (e.g., "Winter Break", "Annual Sports Day", "Mid-term Exams").
        description (str): Optional detailed description of the event.
        start_date (datetime): Event start date and time.
        end_date (datetime): Event end date and time (for multi-day events).
        type (str): Event category - uses EventType enum values (default: EVENT).
    """
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)  # Event name
    description = Column(String, nullable=True)  # Optional event details
    start_date = Column(DateTime, nullable=False)  # Event start datetime
    end_date = Column(DateTime, nullable=False)  # Event end datetime (can be same as start for single-day events)
    type = Column(String, default=EventType.EVENT)  # Event category (holiday/exam/event)
