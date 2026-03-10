"""CRUD operations for classroom management.

This module handles class/section organization and teacher assignments.
Classes group students and are used throughout the system for academic operations.
"""

from sqlalchemy.orm import Session
from app.models.class_room import ClassRoom
from app.schemas.class_room import ClassRoomCreate, ClassRoomUpdate


def get_class_room(db: Session, class_room_id: str):
    """Retrieve a classroom by its unique identifier.
    
    Args:
        db: Database session for query execution.
        class_room_id: Unique identifier of the classroom.
        
    Returns:
        ClassRoom object if found, None otherwise.
    """
    return db.query(ClassRoom).filter(ClassRoom.id == class_room_id).first()


def get_class_room_by_name(db: Session, name: str):
    """Retrieve a classroom by its name.
    
    Used for duplicate checking and lookup operations.
    
    Args:
        db: Database session for query execution.
        name: Name of the classroom (e.g., "10-A", "Grade 5-B").
        
    Returns:
        ClassRoom object if found, None otherwise.
    """
    return db.query(ClassRoom).filter(ClassRoom.name == name).first()


def get_class_rooms(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a paginated list of all classrooms.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of ClassRoom objects.
    """
    return db.query(ClassRoom).offset(skip).limit(limit).all()


def get_class_rooms_by_teacher(db: Session, teacher_id: str, skip: int = 0, limit: int = 100):
    """Retrieve all classrooms assigned to a specific teacher.
    
    Args:
        db: Database session for query execution.
        teacher_id: Unique identifier of the teacher.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of ClassRoom objects assigned to the teacher.
    """
    return db.query(ClassRoom).filter(ClassRoom.teacher_id == teacher_id).offset(skip).limit(limit).all()


def create_class_room(db: Session, class_room: ClassRoomCreate):
    """Create a new classroom with teacher assignment.
    
    Args:
        db: Database session for query execution.
        class_room: ClassRoomCreate schema with name and teacher_id.
        
    Returns:
        Newly created ClassRoom object with generated ID.
    """
    db_class_room = ClassRoom(name=class_room.name, teacher_id=class_room.teacher_id)
    db.add(db_class_room)
    db.commit()
    db.refresh(db_class_room)
    return db_class_room


def update_class_room(db: Session, db_class_room: ClassRoom, class_room_update: ClassRoomUpdate):
    """Update an existing classroom.
    
    Supports partial updates for name changes or teacher reassignment.
    
    Args:
        db: Database session for query execution.
        db_class_room: Existing ClassRoom object to update.
        class_room_update: ClassRoomUpdate schema with fields to update.
        
    Returns:
        Updated ClassRoom object.
    """
    update_data = class_room_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_class_room, key, value)
    db.add(db_class_room)
    db.commit()
    db.refresh(db_class_room)
    return db_class_room


def delete_class_room(db: Session, class_room_id: str):
    """Permanently delete a classroom.
    
    Args:
        db: Database session for query execution.
        class_room_id: Unique identifier of the classroom to delete.
        
    Returns:
        Deleted ClassRoom object if found and deleted, None otherwise.
        
    Warning:
        Deleting a classroom affects students, timetables, and assignments.
    """
    db_class_room = db.query(ClassRoom).filter(ClassRoom.id == class_room_id).first()
    if db_class_room:
        db.delete(db_class_room)
        db.commit()
    return db_class_room