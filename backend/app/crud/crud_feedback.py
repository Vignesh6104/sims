from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.feedback import Feedback, FeedbackStatus
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate

def get_feedback(db: Session, feedback_id: str):
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()

def get_feedbacks(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[FeedbackStatus] = None
):
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
        status=FeedbackStatus.OPEN
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
    if feedback_update.status:
        db_feedback.status = feedback_update.status
    if feedback_update.admin_response:
        db_feedback.admin_response = feedback_update.admin_response
    if feedback_update.priority:
        db_feedback.priority = feedback_update.priority
        
    db.commit()
    db.refresh(db_feedback)
    return db_feedback
