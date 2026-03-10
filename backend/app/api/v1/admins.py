"""
Administrator Management API Endpoints.

This module provides CRUD (Create, Read, Update, Delete) operations for
system administrators. All endpoints require superuser authentication.

Admin accounts have the highest privilege level in the system and can:
- Create and manage other admin accounts
- Access all system resources
- Manage teachers, students, and parents
- Configure system settings

Authentication Required:
    All endpoints require superuser (admin) authentication via Bearer token.

Authorization:
    Only superusers can access these endpoints.
    Regular admins cannot create or delete other admins.
"""
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
    Retrieve list of all administrators with pagination.
    
    Superuser-only endpoint to view all admin accounts in the system.
    Supports pagination to handle large datasets efficiently.
    
    Query Parameters:
        skip (int): Number of records to skip (default: 0)
        limit (int): Maximum number of records to return (default: 100, max: 100)
        
    Authentication:
        Requires: Superuser (Admin) role with valid Bearer token
        
    Returns:
        List[Admin]: List of admin objects with profile information
        
    HTTP Status Codes:
        200: Successfully retrieved admin list
        401: Unauthorized (invalid/missing token)
        403: Forbidden (not a superuser)
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
    Create a new administrator account.
    
    Only existing superusers can create new admin accounts.
    Validates that the email is unique before creation.
    
    Request Body:
        AdminCreate schema containing:
        - email (str): Unique email address for the admin
        - password (str): Plain text password (will be hashed)
        - full_name (str): Administrator's full name
        - is_superuser (bool, optional): Grant superuser privileges
        
    Authentication:
        Requires: Superuser (Admin) role with valid Bearer token
        
    Returns:
        Admin: The newly created admin object
        
    Raises:
        HTTPException 400: Admin with email already exists
        
    HTTP Status Codes:
        200: Admin successfully created
        400: Duplicate email
        401: Unauthorized
        403: Forbidden (not a superuser)
    """
    # Check for duplicate email
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
    Get current authenticated admin's profile.
    
    Returns the profile information of the currently authenticated superuser.
    Useful for displaying user info in the UI or verification purposes.
    
    Authentication:
        Requires: Superuser (Admin) role with valid Bearer token
        
    Returns:
        Admin: Current admin's profile data
        
    HTTP Status Codes:
        200: Successfully retrieved profile
        401: Unauthorized (invalid/missing token)
        403: Forbidden (not a superuser)
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
    Update an existing administrator's profile.
    
    Allows superusers to modify admin account details such as name,
    email, password, or superuser status. Only fields provided in the
    request body will be updated (partial updates supported).
    
    Path Parameters:
        admin_id (str): UUID of the admin to update
        
    Request Body:
        AdminUpdate schema (all fields optional):
        - email (str): New email address
        - full_name (str): Updated full name
        - password (str): New password (will be hashed)
        - is_active (bool): Account active status
        - is_superuser (bool): Superuser privileges
        
    Authentication:
        Requires: Superuser (Admin) role with valid Bearer token
        
    Returns:
        Admin: The updated admin object
        
    Raises:
        HTTPException 404: Admin not found
        
    HTTP Status Codes:
        200: Admin successfully updated
        404: Admin not found
        401: Unauthorized
        403: Forbidden (not a superuser)
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
    Delete an administrator account permanently.
    
    Permanently removes an admin from the system. Includes safety check
    to prevent self-deletion which could lock you out of the system.
    
    Path Parameters:
        admin_id (str): UUID of the admin to delete
        
    Authentication:
        Requires: Superuser (Admin) role with valid Bearer token
        
    Returns:
        Admin: The deleted admin object (for confirmation/logging)
        
    Raises:
        HTTPException 404: Admin not found
        HTTPException 400: Attempting to delete current admin (self-deletion)
        
    HTTP Status Codes:
        200: Admin successfully deleted
        400: Cannot delete current admin
        404: Admin not found
        401: Unauthorized
        403: Forbidden (not a superuser)
        
    Warning:
        This operation is permanent and cannot be undone.
        All related data may be affected based on database constraints.
    """
    admin = crud_admin.get_admin(db, admin_id=admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Safety check: Prevent deleting the currently authenticated admin
    if admin.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete current admin")
        
    db.delete(admin)
    db.commit()
    return admin
