"""CRUD operations for feedback and complaint management.

This module handles feedback submission from students, teachers, and parents
with priority levels, status tracking, and admin response functionality.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.feedback import Feedback, FeedbackStatus
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate


def get_feedback(db: Session, feedback_id: str):
    """Retrieve a single feedback entry by its unique identifier.
    
    Args:
        db: Database session for query execution.
        feedback_id: Unique identifier of the feedback.
        
    Returns:
        Feedback object if found, None otherwise.
    """
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def get_feedbacks(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[FeedbackStatus] = None
):
    """Retrieve all feedback entries with optional status filtering.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        status: Optional filter by feedback status (OPEN, IN_PROGRESS, RESOLVED).
        
    Returns:
        List of Feedback objects matching filter criteria.
    """
    query = db.query(Feedback)
    if status:
        query = query.filter(Feedback.status == status)
    return query.offset(skip).limit(limit).all()


def get_user_feedbacks(
    db: Session,
    user_id: str,
    role: str,
    skip: int = 0,
    limit: int = 100
):
    """Retrieve all feedback submitted by a specific user.
    
    Filters by role to determine which ID field to query.
    
    Args:
        db: Database session for query execution.
        user_id: Unique identifier of the user.
        role: User's role ("student", "teacher", or "parent").
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Feedback objects submitted by the user.
        
    Note:
        Role-based filtering: Queries different ID fields based on user role.
    """
    query = db.query(Feedback)
    if role == "student":
        query = query.filter(Feedback.student_id == user_id)
    elif role == "teacher":
        query = query.filter(Feedback.teacher_id == user_id)
    elif role == "parent":
        query = query.filter(Feedback.parent_id == user_id)
        
    return query.offset(skip).limit(limit).all()


def create_feedback(
    db: Session, 
    feedback: FeedbackCreate, 
    user_id: str, 
    role: str
):
    """Create a new feedback submission.
    
    Automatically assigns feedback to the correct user type (student/teacher/parent)
    based on role and sets initial status to OPEN.
    
    Args:
        db: Database session for query execution.
        feedback: FeedbackCreate schema with feedback details.
        user_id: Unique identifier of the user submitting feedback.
        role: User's role ("student", "teacher", or "parent").
        
    Returns:
        Newly created Feedback object with generated ID and OPEN status.
        
    Note:
        Role-based assignment: Populates appropriate ID field based on role.
        Status is always initialized to OPEN.
    """
    # Determine which ID field to populate based on role
    student_id = user_id if role == "student" else None
    teacher_id = user_id if role == "teacher" else None
    parent_id = user_id if role == "parent" else None
    
    db_feedback = Feedback(
        student_id=student_id,
        teacher_id=teacher_id,
        parent_id=parent_id,
        subject=feedback.subject,
        description=feedback.description,
        priority=feedback.priority,
        status=FeedbackStatus.OPEN  # Initial status is always OPEN
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def update_feedback(
    db: Session, 
    db_feedback: Feedback, 
    feedback_update: FeedbackUpdate
):
    """Update feedback status, admin response, or priority.
    
    Used by administrators to manage and respond to feedback.
    
    Args:
        db: Database session for query execution.
        db_feedback: Existing Feedback object to update.
        feedback_update: FeedbackUpdate schema with fields to update.
        
    Returns:
        Updated Feedback object.
        
    Note:
        Only updates provided fields (status, admin_response, and/or priority).
    """
    if feedback_update.status:
        db_feedback.status = feedback_update.status
    if feedback_update.admin_response:
        db_feedback.admin_response = feedback_update.admin_response
    if feedback_update.priority:
        db_feedback.priority = feedback_update.priority
        
    db.commit()
    db.refresh(db_feedback)
    return db_feedback
