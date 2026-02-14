from typing import List, Optional, Union
from sqlalchemy.orm import Session
from app.models.leave import Leave, LeaveStatus
from app.schemas.leave import LeaveCreate, LeaveUpdate

def get_leave(db: Session, leave_id: str):
    return db.query(Leave).filter(Leave.id == leave_id).first()

def get_leaves(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    student_id: Optional[str] = None, 
    teacher_id: Optional[str] = None,
    status: Optional[LeaveStatus] = None
):
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
        status=LeaveStatus.PENDING
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
    if leave_update.status:
        db_leave.status = leave_update.status
    if leave_update.rejection_reason is not None:
        db_leave.rejection_reason = leave_update.rejection_reason
        
    db.commit()
    db.refresh(db_leave)
    return db_leave

def delete_leave(db: Session, leave_id: str):
    db_leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if db_leave:
        db.delete(db_leave)
        db.commit()
    return db_leave
