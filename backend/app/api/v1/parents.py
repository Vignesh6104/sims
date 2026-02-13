from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_parent, crud_student
from app.schemas.parent import Parent, ParentCreate
from app.schemas.student import Student

router = APIRouter()

@router.get("/", response_model=List[Parent])
def read_parents(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    return crud_parent.get_parents(db, skip=skip, limit=limit)

@router.post("/", response_model=Parent)
def create_parent(
    *,
    db: Session = Depends(deps.get_db),
    parent_in: ParentCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    parent = crud_parent.get_parent_by_email(db, email=parent_in.email)
    if parent:
        raise HTTPException(status_code=400, detail="Parent already exists")
    return crud_parent.create_parent(db, parent=parent_in)

@router.get("/me", response_model=Parent)
def read_parent_me(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    # Assuming current_user is the parent object if logged in as parent
    return current_user

@router.get("/my-children", response_model=List[Student])
def read_my_children(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user), # Must be parent
) -> Any:
    # return children linked to this parent
    # Since we defined the relationship in the model, we can access it directly via the ORM
    # However, `current_user` from `get_current_active_user` might be a generic dict or specific model depending on impl.
    # We need to ensure `deps.get_current_active_user` supports Parent role.
    
    # Reloading user from DB to ensure relationships are loaded if needed
    parent = crud_parent.get_parent(db, parent_id=current_user.id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    return parent.students
