"""CRUD operations for school event management.

This module handles creation, retrieval, and deletion of school events
including holidays, sports days, parent-teacher meetings, and other activities.
"""

from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate


def get_event(db: Session, event_id: str):
    """Retrieve a single event by its unique identifier.
    
    Args:
        db: Database session for query execution.
        event_id: Unique identifier of the event.
        
    Returns:
        Event object if found, None otherwise.
    """
    return db.query(Event).filter(Event.id == event_id).first()


def get_events(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve all events ordered by start date.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Event objects ordered by start_date (chronological).
        
    Note:
        Events are automatically ordered by start date for calendar view.
    """
    return db.query(Event).order_by(Event.start_date).offset(skip).limit(limit).all()


def create_event(db: Session, event: EventCreate):
    """Create a new school event.
    
    Args:
        db: Database session for query execution.
        event: EventCreate schema with event details.
        
    Returns:
        Newly created Event object with generated ID.
    """
    db_event = Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: str):
    """Permanently delete an event.
    
    Args:
        db: Database session for query execution.
        event_id: Unique identifier of the event to delete.
        
    Returns:
        Deleted Event object if found and deleted, None otherwise.
    """
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event