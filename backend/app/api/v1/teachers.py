from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_teacher
from app.schemas.teacher import Teacher, TeacherCreate, TeacherUpdate

router = APIRouter()

@router.get("/", response_model=List[Teacher])
def read_teachers(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Retrieve teachers.
    """
    return crud_teacher.get_teachers(db, skip=skip, limit=limit)

@router.post("/", response_model=Teacher)
def create_teacher(
    *,
    db: Session = Depends(deps.get_db),
    teacher_in: TeacherCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Create new teacher profile (Admin only).
    """
    teacher = crud_teacher.get_teacher_by_email(db, email=teacher_in.email)
    if teacher:
        raise HTTPException(status_code=400, detail="Teacher already exists")
    return crud_teacher.create_teacher(db, teacher=teacher_in)

@router.get("/{teacher_id}", response_model=Teacher)
def read_teacher(
    teacher_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get teacher by ID.
    """
    teacher = crud_teacher.get_teacher(db, teacher_id=teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.put("/{teacher_id}", response_model=Teacher)
def update_teacher(
    *,
    db: Session = Depends(deps.get_db),
    teacher_id: str,
    teacher_in: TeacherUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Update teacher.
    """
    teacher = crud_teacher.get_teacher(db, teacher_id=teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher = crud_teacher.update_teacher(db, db_teacher=teacher, teacher_update=teacher_in)
    return teacher

@router.delete("/{teacher_id}", response_model=Teacher)
def delete_teacher(
    *,
    db: Session = Depends(deps.get_db),
    teacher_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Delete teacher.
    """
    teacher = crud_teacher.get_teacher(db, teacher_id=teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher = crud_teacher.delete_teacher(db, teacher_id=teacher_id)
    return teacher
