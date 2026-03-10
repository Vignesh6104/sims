"""CRUD operations for subject management.

This module handles subject catalog maintenance including subject codes
and names. Subjects are used across the system for timetables, exams, and marks.
"""

from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


def get_subject(db: Session, subject_id: str):
    """Retrieve a subject by its unique identifier.
    
    Args:
        db: Database session for query execution.
        subject_id: Unique identifier of the subject.
        
    Returns:
        Subject object if found, None otherwise.
    """
    return db.query(Subject).filter(Subject.id == subject_id).first()


def get_subject_by_name(db: Session, name: str):
    """Retrieve a subject by its name.
    
    Used for duplicate checking and lookup operations.
    
    Args:
        db: Database session for query execution.
        name: Name of the subject to search for.
        
    Returns:
        Subject object if found, None otherwise.
    """
    return db.query(Subject).filter(Subject.name == name).first()


def get_subjects(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a paginated list of all subjects.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Subject objects.
    """
    return db.query(Subject).offset(skip).limit(limit).all()


def create_subject(db: Session, subject: SubjectCreate):
    """Create a new subject.
    
    Args:
        db: Database session for query execution.
        subject: SubjectCreate schema with name and code.
        
    Returns:
        Newly created Subject object with generated ID.
    """
    db_subject = Subject(name=subject.name, code=subject.code)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def update_subject(db: Session, db_subject: Subject, subject_update: SubjectUpdate):
    """Update an existing subject.
    
    Supports partial updates for name or code changes.
    
    Args:
        db: Database session for query execution.
        db_subject: Existing Subject object to update.
        subject_update: SubjectUpdate schema with fields to update.
        
    Returns:
        Updated Subject object.
    """
    update_data = subject_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_subject, key, value)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def delete_subject(db: Session, subject_id: str):
    """Permanently delete a subject.
    
    Args:
        db: Database session for query execution.
        subject_id: Unique identifier of the subject to delete.
        
    Returns:
        Deleted Subject object if found and deleted, None otherwise.
        
    Warning:
        Deleting a subject may affect timetables, marks, and other records.
    """
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if db_subject:
        db.delete(db_subject)
        db.commit()
    return db_subject
