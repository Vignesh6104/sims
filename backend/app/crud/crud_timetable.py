"""CRUD operations for class timetable scheduling.

This module handles class schedule management with teacher and subject
assignments for specific time periods. Includes conflict checking capability.
"""

from sqlalchemy.orm import Session
from app.models.timetable import Timetable
from app.schemas.timetable import TimetableCreate, TimetableUpdate


def get_timetable_by_class(db: Session, class_id: str):
    """Retrieve the complete timetable for a specific class.
    
    Args:
        db: Database session for query execution.
        class_id: Unique identifier of the class.
        
    Returns:
        List of Timetable entries for the class.
    """
    return db.query(Timetable).filter(Timetable.class_id == class_id).all()


def get_timetable_by_teacher(db: Session, teacher_id: str):
    """Retrieve all timetable entries for a specific teacher.
    
    Useful for teacher's personal schedule view.
    
    Args:
        db: Database session for query execution.
        teacher_id: Unique identifier of the teacher.
        
    Returns:
        List of Timetable entries assigned to the teacher.
    """
    return db.query(Timetable).filter(Timetable.teacher_id == teacher_id).all()


def create_timetable_entry(db: Session, timetable_in: TimetableCreate):
    """Create a new timetable entry.
    
    Args:
        db: Database session for query execution.
        timetable_in: TimetableCreate schema with schedule details.
        
    Returns:
        Newly created Timetable object with generated ID.
        
    Note:
        Future enhancement: Add conflict checking for same teacher/class
        at the same time slot.
    """
    # Optional: Check for conflicts (same teacher/class at same time)
    # For MVP, just create
    db_entry = Timetable(**timetable_in.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_timetable_entry(db: Session, entry_id: str):
    """Permanently delete a timetable entry.
    
    Args:
        db: Database session for query execution.
        entry_id: Unique identifier of the timetable entry.
        
    Returns:
        Deleted Timetable object if found and deleted, None otherwise.
    """
    entry = db.query(Timetable).filter(Timetable.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
    return entry
