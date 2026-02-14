from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.feedback import FeedbackStatus
from app.schemas.feedback import Feedback, FeedbackCreate, FeedbackUpdate
from app.crud import crud_feedback

router = APIRouter()

@router.post("/", response_model=Feedback)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Submit feedback/grievance (Student, Teacher, Parent).
    """
    role = None
    if current_user.__class__.__name__ == "Student":
        role = "student"
    elif current_user.__class__.__name__ == "Teacher":
        role = "teacher"
    elif current_user.__class__.__name__ == "Parent":
        role = "parent"
            
    if not role:
         raise HTTPException(status_code=400, detail="Only Students, Teachers, and Parents can submit feedback.")

    return crud_feedback.create_feedback(db=db, feedback=feedback_in, user_id=str(current_user.id), role=role)

@router.get("/", response_model=List[Feedback])
def read_feedbacks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[FeedbackStatus] = None,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve feedbacks.
    - Admins: View all.
    - Others: View their own.
    """
    role = current_user.__class__.__name__
    
    if role == "Admin":
        return crud_feedback.get_feedbacks(db, skip=skip, limit=limit, status=status)
    else:
        # Map class name to role string used in CRUD
        role_str = role.lower()
        return crud_feedback.get_user_feedbacks(db, user_id=str(current_user.id), role=role_str, skip=skip, limit=limit)

@router.put("/{feedback_id}", response_model=Feedback)
def update_feedback(
    feedback_id: str,
    feedback_in: FeedbackUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admins
) -> Any:
    """
    Update feedback (Admin response/Status change).
    """
    feedback = crud_feedback.get_feedback(db, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
        
    feedback = crud_feedback.update_feedback(db=db, db_feedback=feedback, feedback_update=feedback_in)
    return feedback
