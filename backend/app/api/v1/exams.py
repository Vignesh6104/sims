from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_exam
from app.schemas.exam import Exam, ExamCreate, ExamUpdate

router = APIRouter()

@router.get("/", response_model=List[Exam])
def read_exams(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve exams.
    """
    return crud_exam.get_exams(db, skip=skip, limit=limit)

@router.post("/", response_model=Exam)
def create_exam(
    *,
    db: Session = Depends(deps.get_db),
    exam_in: ExamCreate,
    current_user: Any = Depends(deps.get_current_active_staff), # Staff only
) -> Any:
    """
    Create new exam.
    """
    return crud_exam.create_exam(db, exam=exam_in)

@router.get("/{exam_id}", response_model=Exam)
def read_exam(
    exam_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get exam by ID.
    """
    exam = crud_exam.get_exam(db, exam_id=exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

@router.put("/{exam_id}", response_model=Exam)
def update_exam(
    *,
    db: Session = Depends(deps.get_db),
    exam_id: str,
    exam_in: ExamUpdate,
    current_user: Any = Depends(deps.get_current_active_staff), # Staff only
) -> Any:
    """
    Update exam.
    """
    exam = crud_exam.get_exam(db, exam_id=exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return crud_exam.update_exam(db, db_exam=exam, exam_update=exam_in)

@router.delete("/{exam_id}", response_model=Exam)
def delete_exam(
    *,
    db: Session = Depends(deps.get_db),
    exam_id: str,
    current_user: Any = Depends(deps.get_current_active_staff), # Staff only
) -> Any:
    """
    Delete exam.
    """
    exam = crud_exam.get_exam(db, exam_id=exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return crud_exam.delete_exam(db, exam_id=exam_id)
