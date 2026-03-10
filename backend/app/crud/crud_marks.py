"""CRUD operations for student marks and academic performance tracking.

This module handles exam marks entry, retrieval, and reporting with
advanced filtering capabilities and grade calculation features.
"""

from sqlalchemy.orm import Session
from app.models.marks import Mark
from app.models.student import Student
from app.models.exam import Exam
from app.schemas.marks import MarkCreate, MarkUpdate


def get_mark(db: Session, mark_id: str):
    """Retrieve a single mark entry by its unique identifier.
    
    Args:
        db: Database session for query execution.
        mark_id: Unique identifier of the mark.
        
    Returns:
        Mark object if found, None otherwise.
    """
    return db.query(Mark).filter(Mark.id == mark_id).first()


def get_marks_by_student(db: Session, student_id: str, skip: int = 0, limit: int = 100):
    """Retrieve all marks for a specific student.
    
    Args:
        db: Database session for query execution.
        student_id: Unique identifier of the student.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Mark objects for the specified student.
    """
    return db.query(Mark).filter(Mark.student_id == student_id).offset(skip).limit(limit).all()


def get_marks_by_filters(db: Session, student_ids: list[str], exam_id: str, subject: str):
    """Retrieve marks using multiple filter criteria.
    
    Useful for bulk operations like class-wise grade entry or analysis.
    
    Args:
        db: Database session for query execution.
        student_ids: List of student IDs to filter by.
        exam_id: Exam identifier to filter by.
        subject: Subject name to filter by.
        
    Returns:
        List of Mark objects matching all filter criteria.
        
    Note:
        Uses SQL IN clause for efficient multi-student queries.
    """
    return db.query(Mark).filter(
        Mark.student_id.in_(student_ids),
        Mark.exam_id == exam_id,
        Mark.subject == subject
    ).all()


def create_mark(db: Session, mark: MarkCreate):
    """Create a new mark entry for a student.
    
    Args:
        db: Database session for query execution.
        mark: MarkCreate schema with mark details.
        
    Returns:
        Newly created Mark object with generated ID.
    """
    db_mark = Mark(**mark.model_dump())
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    return db_mark


def update_mark(db: Session, db_mark: Mark, mark_update: MarkUpdate):
    """Update an existing mark entry.
    
    Supports partial updates for corrections or grade adjustments.
    
    Args:
        db: Database session for query execution.
        db_mark: Existing Mark object to update.
        mark_update: MarkUpdate schema with fields to update.
        
    Returns:
        Updated Mark object.
    """
    update_data = mark_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mark, key, value)
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    return db_mark


def get_marks_report(db: Session, class_id: str):
    """Generate a comprehensive marks report for a class.
    
    Performs a three-way JOIN between Mark, Student, and Exam tables
    to create a detailed performance report with calculated percentages.
    
    Args:
        db: Database session for query execution.
        class_id: Unique identifier of the class.
        
    Returns:
        List of dictionaries containing:
            - student_name: Full name of the student
            - roll_number: Student's roll number
            - exam_name: Name of the exam
            - date: Exam date
            - subject: Subject name
            - score: Marks obtained
            - max_score: Maximum possible marks
            - percentage: Calculated percentage (rounded to 2 decimals)
            
    Note:
        Complex JOIN query: Mark -> Student -> Exam with class filtering.
        Percentage calculation includes division-by-zero protection.
    """
    # Multi-table JOIN to gather comprehensive exam data
    results = db.query(Mark, Student, Exam).join(Student, Mark.student_id == Student.id).join(Exam, Mark.exam_id == Exam.id).filter(Student.class_id == class_id).all()
    
    report = []
    for mark, student, exam in results:
        report.append({
            "student_name": student.full_name,
            "roll_number": student.roll_number,
            "exam_name": exam.name,
            "date": exam.date,
            "subject": mark.subject,
            "score": mark.score,
            "max_score": mark.max_score,
            # Calculate percentage with zero-division protection
            "percentage": round((mark.score / mark.max_score) * 100, 2) if mark.max_score > 0 else 0
        })
    return report