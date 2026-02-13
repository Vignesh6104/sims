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

@router.put("/{admin_id}", response_model=Admin)
def update_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_id: str,
    admin_in: AdminUpdate,
    current_user: Admin = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an admin. Only for superusers.
    """
    admin = crud_admin.get_admin(db, admin_id=admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return crud_admin.update_admin(db, db_admin=admin, admin_update=admin_in)

@router.delete("/{admin_id}", response_model=Admin)
def delete_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_id: str,
    current_user: Admin = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an admin. Only for superusers.
    """
    admin = crud_admin.get_admin(db, admin_id=admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Prevent deleting the current user
    if admin.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete current admin")
        
    db.delete(admin)
    db.commit()
    return admin
