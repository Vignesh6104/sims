"""CRUD operations for Student user management.

This module handles all database operations for student accounts including
registration, class assignment, and academic profile management.
"""

from sqlalchemy.orm import Session
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.core.security import get_password_hash


def get_student(db: Session, student_id: str):
    """Retrieve a student by their unique identifier.
    
    Args:
        db: Database session for query execution.
        student_id: Unique identifier of the student.
        
    Returns:
        Student object if found, None otherwise.
    """
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_email(db: Session, email: str):
    """Retrieve a student by their email address.
    
    Used for authentication and duplicate checking.
    
    Args:
        db: Database session for query execution.
        email: Email address to search for.
        
    Returns:
        Student object if found, None otherwise.
    """
    return db.query(Student).filter(Student.email == email).first()


def get_students(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a paginated list of all students.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Student objects.
    """
    return db.query(Student).offset(skip).limit(limit).all()


def get_students_by_class(db: Session, class_id: str, skip: int = 0, limit: int = 100):
    """Retrieve all students in a specific class.
    
    Useful for class-specific operations like attendance, assignments, etc.
    
    Args:
        db: Database session for query execution.
        class_id: Unique identifier of the class.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Student objects belonging to the specified class.
    """
    return db.query(Student).filter(Student.class_id == class_id).offset(skip).limit(limit).all()


def create_student(db: Session, student: StudentCreate):
    """Create a new student account with hashed password.
    
    Args:
        db: Database session for query execution.
        student: StudentCreate schema with student details.
        
    Returns:
        Newly created Student object with generated ID.
        
    Note:
        Password is automatically hashed before storage.
        Roll number should be unique per class.
    """
    # Hash the password for secure storage
    hashed_password = get_password_hash(student.password)
    db_student = Student(
        email=student.email,
        hashed_password=hashed_password,
        full_name=student.full_name,
        roll_number=student.roll_number,
        date_of_birth=student.date_of_birth,
        address=student.address,
        class_id=student.class_id,
        is_active=student.is_active
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, db_student: Student, student_update: StudentUpdate):
    """Update existing student information.
    
    Supports partial updates. Password updates are automatically hashed.
    
    Args:
        db: Database session for query execution.
        db_student: Existing Student object to update.
        student_update: StudentUpdate schema with fields to update.
        
    Returns:
        Updated Student object.
        
    Note:
        Only provided fields are updated. Password is hashed if included.
    """
    update_data = student_update.model_dump(exclude_unset=True)
    # Special handling for password updates
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        db_student.hashed_password = hashed_password
        
    for key, value in update_data.items():
        setattr(db_student, key, value)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: str):
    """Permanently delete a student account.
    
    Args:
        db: Database session for query execution.
        student_id: Unique identifier of the student to delete.
        
    Returns:
        Deleted Student object if found and deleted, None otherwise.
        
    Warning:
        This is a permanent deletion. Consider soft delete for production.
        Deleting a student may affect related records like marks, attendance, etc.
    """
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
    return db_student