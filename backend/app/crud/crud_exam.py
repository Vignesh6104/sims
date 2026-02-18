"""CRUD operations for exam management.

This module handles exam scheduling, updates, and deletion.
Exams are referenced by marks records for performance tracking.
"""

from sqlalchemy.orm import Session
from app.models.exam import Exam
from app.schemas.exam import ExamCreate, ExamUpdate


def get_exam(db: Session, exam_id: str):
    """Retrieve a single exam by its unique identifier.
    
    Args:
        db: Database session for query execution.
        exam_id: Unique identifier of the exam.
        
    Returns:
        Exam object if found, None otherwise.
    """
    return db.query(Exam).filter(Exam.id == exam_id).first()


def get_exams(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a paginated list of all exams.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Exam objects.
    """
    return db.query(Exam).offset(skip).limit(limit).all()


def create_exam(db: Session, exam: ExamCreate):
    """Create a new exam entry.
    
    Args:
        db: Database session for query execution.
        exam: ExamCreate schema with exam details (name and date).
        
    Returns:
        Newly created Exam object with generated ID.
    """
    db_exam = Exam(name=exam.name, date=exam.date)
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam


def update_exam(db: Session, db_exam: Exam, exam_update: ExamUpdate):
    """Update an existing exam.
    
    Supports partial updates for rescheduling or name changes.
    
    Args:
        db: Database session for query execution.
        db_exam: Existing Exam object to update.
        exam_update: ExamUpdate schema with fields to update.
        
    Returns:
        Updated Exam object.
    """
    update_data = exam_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exam, key, value)
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam


def delete_exam(db: Session, exam_id: str):
    """Permanently delete an exam.
    
    Args:
        db: Database session for query execution.
        exam_id: Unique identifier of the exam to delete.
        
    Returns:
        Deleted Exam object if found and deleted, None otherwise.
        
    Warning:
        Deleting an exam may affect related marks records.
    """
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if db_exam:
        db.delete(db_exam)
        db.commit()
    return db_exam
