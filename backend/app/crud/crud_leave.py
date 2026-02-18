"""CRUD operations for leave application management.

This module handles leave requests from students and teachers with
approval workflow, status tracking, and role-based filtering.
"""

from typing import List, Optional, Union
from sqlalchemy.orm import Session
from app.models.leave import Leave, LeaveStatus
from app.schemas.leave import LeaveCreate, LeaveUpdate


def get_leave(db: Session, leave_id: str):
    """Retrieve a single leave application by its unique identifier.
    
    Args:
        db: Database session for query execution.
        leave_id: Unique identifier of the leave application.
        
    Returns:
        Leave object if found, None otherwise.
    """
    return db.query(Leave).filter(Leave.id == leave_id).first()


def get_leaves(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    student_id: Optional[str] = None, 
    teacher_id: Optional[str] = None,
    status: Optional[LeaveStatus] = None
):
    """Retrieve leave applications with optional filtering.
    
    Supports filtering by student, teacher, and approval status.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        student_id: Optional filter by student ID (default: None).
        teacher_id: Optional filter by teacher ID (default: None).
        status: Optional filter by leave status (PENDING, APPROVED, REJECTED).
        
    Returns:
        List of Leave objects matching filter criteria.
        
    Note:
        Multiple filters can be combined for complex queries.
    """
    query = db.query(Leave)
    if student_id:
        query = query.filter(Leave.student_id == student_id)
    if teacher_id:
        query = query.filter(Leave.teacher_id == teacher_id)
    if status:
        query = query.filter(Leave.status == status)
        
    return query.offset(skip).limit(limit).all()


def create_leave(
    db: Session, 
    leave: LeaveCreate, 
    user_id: str, 
    role: str
):
    """Create a new leave application.
    
    Automatically assigns the leave to the correct user type (student/teacher)
    based on role and sets initial status to PENDING.
    
    Args:
        db: Database session for query execution.
        leave: LeaveCreate schema with leave details.
        user_id: Unique identifier of the user applying for leave.
        role: User's role ("student" or "teacher").
        
    Returns:
        Newly created Leave object with generated ID and PENDING status.
        
    Note:
        Role-based assignment: Populates student_id or teacher_id based on role.
        Status is always initialized to PENDING.
    """
    # Determine which ID field to populate based on role
    student_id = user_id if role == "student" else None
    teacher_id = user_id if role == "teacher" else None
    
    db_leave = Leave(
        student_id=student_id,
        teacher_id=teacher_id,
        start_date=leave.start_date,
        end_date=leave.end_date,
        reason=leave.reason,
        leave_type=leave.leave_type,
        status=LeaveStatus.PENDING  # Initial status is always PENDING
    )
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave


def update_leave(
    db: Session, 
    db_leave: Leave, 
    leave_update: LeaveUpdate
):
    """Update leave application status and rejection reason.
    
    Used by administrators to approve or reject leave applications.
    
    Args:
        db: Database session for query execution.
        db_leave: Existing Leave object to update.
        leave_update: LeaveUpdate schema with status and optional rejection reason.
        
    Returns:
        Updated Leave object.
        
    Note:
        Only updates provided fields (status and/or rejection_reason).
    """
    if leave_update.status:
        db_leave.status = leave_update.status
    if leave_update.rejection_reason is not None:
        db_leave.rejection_reason = leave_update.rejection_reason
        
    db.commit()
    db.refresh(db_leave)
    return db_leave


def delete_leave(db: Session, leave_id: str):
    """Permanently delete a leave application.
    
    Args:
        db: Database session for query execution.
        leave_id: Unique identifier of the leave application.
        
    Returns:
        Deleted Leave object if found and deleted, None otherwise.
    """
    db_leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if db_leave:
        db.delete(db_leave)
        db.commit()
    return db_leave
