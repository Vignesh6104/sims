from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_timetable
from app.schemas.timetable import Timetable, TimetableCreate

router = APIRouter()

@router.get("/class/{class_id}", response_model=List[Timetable])
def read_class_timetable(
    class_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_timetable.get_timetable_by_class(db, class_id=class_id)

@router.get("/teacher/{teacher_id}", response_model=List[Timetable])
def read_teacher_timetable(
    teacher_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_timetable.get_timetable_by_teacher(db, teacher_id=teacher_id)

@router.post("/", response_model=Timetable)
def create_timetable_entry(
    *,
    db: Session = Depends(deps.get_db),
    timetable_in: TimetableCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin only
) -> Any:
    return crud_timetable.create_timetable_entry(db, timetable_in=timetable_in)

@router.delete("/{entry_id}", response_model=Timetable)
def delete_timetable_entry(
    entry_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    return crud_timetable.delete_timetable_entry(db, entry_id=entry_id)
