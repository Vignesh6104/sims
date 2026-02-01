from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_notification
from app.schemas.notification import Notification, NotificationCreate

router = APIRouter()

@router.get("/", response_model=List[Notification])
def read_my_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
    # We need to access role from token or user object. 
    # TokenPayload had 'role'. get_current_active_user returns model which doesn't have 'role' string field explicitly on all models matching schema uniformly?
    # Actually User models don't have 'role' column anymore, it was removed. 
    # But auth endpoint sets it. We need to infer it or pass it.
    # For now, let's assume the frontend passes role or we check instance type.
):
    # Determine role
    from app.models.admin import Admin
    from app.models.teacher import Teacher
    from app.models.student import Student
    
    role = "student"
    if isinstance(current_user, Admin): role = "admin"
    elif isinstance(current_user, Teacher): role = "teacher"
    
    return crud_notification.get_notifications_for_user(db, user_id=current_user.id, role=role, skip=skip, limit=limit)

@router.post("/", response_model=Notification)
def send_notification(
    *,
    db: Session = Depends(deps.get_db),
    notification_in: NotificationCreate,
    current_user: Any = Depends(deps.get_current_active_staff), # Teachers/Admins can send
) -> Any:
    return crud_notification.create_notification(db, notification=notification_in)

@router.put("/{notification_id}/read", response_model=Notification)
def mark_read(
    notification_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_notification.mark_notification_read(db, notification_id=notification_id)
