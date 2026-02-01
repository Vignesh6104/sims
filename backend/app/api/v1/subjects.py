from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_subject
from app.schemas.subject import Subject, SubjectCreate, SubjectUpdate

router = APIRouter()

@router.get("/", response_model=List[Subject])
def read_subjects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve subjects.
    """
    return crud_subject.get_subjects(db, skip=skip, limit=limit)

@router.post("/", response_model=Subject)
def create_subject(
    *,
    db: Session = Depends(deps.get_db),
    subject_in: SubjectCreate,
    current_user: Any = Depends(deps.get_current_active_staff), # Teacher can write
) -> Any:
    """
    Create new subject.
    """
    subject = crud_subject.get_subject_by_name(db, name=subject_in.name)
    if subject:
        raise HTTPException(status_code=400, detail="Subject with this name already exists")
    return crud_subject.create_subject(db, subject=subject_in)

@router.get("/{subject_id}", response_model=Subject)
def read_subject(
    subject_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get subject by ID.
    """
    subject = crud_subject.get_subject(db, subject_id=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.put("/{subject_id}", response_model=Subject)
def update_subject(
    *,
    db: Session = Depends(deps.get_db),
    subject_id: str,
    subject_in: SubjectUpdate,
    current_user: Any = Depends(deps.get_current_active_staff), # Teacher can write
) -> Any:
    """
    Update subject.
    """
    subject = crud_subject.get_subject(db, subject_id=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud_subject.update_subject(db, db_subject=subject, subject_update=subject_in)

@router.delete("/{subject_id}", response_model=Subject)
def delete_subject(
    *,
    db: Session = Depends(deps.get_db),
    subject_id: str,
    current_user: Any = Depends(deps.get_current_active_staff), # Teacher can delete
) -> Any:
    """
    Delete subject.
    """
    subject = crud_subject.get_subject(db, subject_id=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud_subject.delete_subject(db, subject_id=subject_id)
