from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_admin
from app.schemas.admin import Admin, AdminCreate, AdminUpdate

router = APIRouter()

@router.get("/", response_model=List[Admin])
def read_admins(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Admin = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve admins. Only for superusers.
    """
    return crud_admin.get_admins(db, skip=skip, limit=limit)

@router.post("/", response_model=Admin)
def create_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: AdminCreate,
    current_user: Admin = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new admin. Only for superusers.
    """
    admin = crud_admin.get_admin_by_email(db, email=admin_in.email)
    if admin:
        raise HTTPException(
            status_code=400,
            detail="The admin with this email already exists.",
        )
    return crud_admin.create_admin(db, admin=admin_in)

@router.get("/me", response_model=Admin)
def read_admin_me(
    current_user: Admin = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get current admin.
    """
    return current_user
