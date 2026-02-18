"""CRUD operations for Teacher user management.

This module handles all database operations for teacher accounts including
authentication, profile management, and qualification tracking.
"""

from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.core.security import get_password_hash


def get_teacher(db: Session, teacher_id: str):
    """Retrieve a teacher by their unique identifier.
    
    Args:
        db: Database session for query execution.
        teacher_id: Unique identifier of the teacher.
        
    Returns:
        Teacher object if found, None otherwise.
    """
    return db.query(Teacher).filter(Teacher.id == teacher_id).first()


def get_teacher_by_email(db: Session, email: str):
    """Retrieve a teacher by their email address.
    
    Used for authentication and preventing duplicate accounts.
    
    Args:
        db: Database session for query execution.
        email: Email address to search for.
        
    Returns:
        Teacher object if found, None otherwise.
    """
    return db.query(Teacher).filter(Teacher.email == email).first()


def get_teachers(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a paginated list of all teachers.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Teacher objects.
    """
    return db.query(Teacher).offset(skip).limit(limit).all()


def create_teacher(db: Session, teacher: TeacherCreate):
    """Create a new teacher account with hashed password.
    
    Args:
        db: Database session for query execution.
        teacher: TeacherCreate schema with teacher details.
        
    Returns:
        Newly created Teacher object with generated ID.
        
    Note:
        Password is automatically hashed before storage.
    """
    # Hash the password for secure storage
    hashed_password = get_password_hash(teacher.password)
    db_teacher = Teacher(
        email=teacher.email,
        hashed_password=hashed_password,
        full_name=teacher.full_name,
        qualification=teacher.qualification,
        subject_specialization=teacher.subject_specialization,
        is_active=teacher.is_active
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


def update_teacher(db: Session, db_teacher: Teacher, teacher_update: TeacherUpdate):
    """Update existing teacher information.
    
    Supports partial updates. Password updates are automatically hashed.
    
    Args:
        db: Database session for query execution.
        db_teacher: Existing Teacher object to update.
        teacher_update: TeacherUpdate schema with fields to update.
        
    Returns:
        Updated Teacher object.
        
    Note:
        Only provided fields are updated. Password is hashed if included.
    """
    update_data = teacher_update.model_dump(exclude_unset=True)
    # Special handling for password updates
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        db_teacher.hashed_password = hashed_password

    for key, value in update_data.items():
        setattr(db_teacher, key, value)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


def delete_teacher(db: Session, teacher_id: str):
    """Permanently delete a teacher account.
    
    Args:
        db: Database session for query execution.
        teacher_id: Unique identifier of the teacher to delete.
        
    Returns:
        Deleted Teacher object if found and deleted, None otherwise.
        
    Warning:
        This is a permanent deletion. Consider soft delete for production.
        Deleting a teacher may affect related records like classes and timetables.
    """
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if db_teacher:
        db.delete(db_teacher)
        db.commit()
    return db_teacher
