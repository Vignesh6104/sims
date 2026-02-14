from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.leave import LeaveStatus
from app.schemas.leave import Leave, LeaveCreate, LeaveUpdate
from app.crud import crud_leave

router = APIRouter()

@router.post("/", response_model=Leave)
def create_leave(
    leave_in: LeaveCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Apply for a leave (Students & Teachers).
    """
    # Assuming role is available on current_user or via token payload if we passed it.
    # But deps.get_current_user returns a model instance (Student, Teacher, etc.)
    # We need to identify the role. 
    # A simple way is to check isinstance, or if the user object has a role attribute.
    # Looking at deps.py, it returns a specific model instance.
    
    role = None
    if hasattr(current_user, "roll_number"): # Loose check for Student
        role = "student"
    elif hasattr(current_user, "qualification"): # Loose check for Teacher
        role = "teacher"
    else:
        # Fallback or check class name
        if current_user.__class__.__name__ == "Student":
            role = "student"
        elif current_user.__class__.__name__ == "Teacher":
            role = "teacher"
            
    if not role:
         raise HTTPException(status_code=400, detail="Only Students and Teachers can apply for leave.")

    return crud_leave.create_leave(db=db, leave=leave_in, user_id=str(current_user.id), role=role)

@router.get("/", response_model=List[Leave])
def read_leaves(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeaveStatus] = None,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve leaves.
    - Admins: View all.
    - Teachers: View their own AND their students (TODO: filter by class).
    - Students: View their own.
    """
    user_role = None
    if current_user.__class__.__name__ == "Admin":
        user_role = "admin"
    elif current_user.__class__.__name__ == "Teacher":
        user_role = "teacher"
    elif current_user.__class__.__name__ == "Student":
        user_role = "student"

    if user_role == "admin":
        return crud_leave.get_leaves(db, skip=skip, limit=limit, status=status)
    elif user_role == "teacher":
        # Teachers see their own leaves. 
        # Ideally they should also see students' leaves to approve them.
        # For this MVP, let's return their own leaves if they request, 
        # OR we can add a query param 'view=student_requests'
        return crud_leave.get_leaves(db, skip=skip, limit=limit, teacher_id=str(current_user.id), status=status)
    elif user_role == "student":
        return crud_leave.get_leaves(db, skip=skip, limit=limit, student_id=str(current_user.id), status=status)
    
    return []

@router.put("/{leave_id}", response_model=Leave)
def update_leave(
    leave_id: str,
    leave_in: LeaveUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff), # Admins & Teachers
) -> Any:
    """
    Update leave status (Approve/Reject).
    """
    leave = crud_leave.get_leave(db, leave_id=leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
        
    # Permission check: Teachers should only approve student leaves, not other teachers'.
    # Admins can do anything.
    if current_user.__class__.__name__ == "Teacher" and leave.teacher_id:
        raise HTTPException(status_code=403, detail="Teachers cannot approve other teachers' leaves.")

    leave = crud_leave.update_leave(db=db, db_leave=leave, leave_update=leave_in)
    return leave
