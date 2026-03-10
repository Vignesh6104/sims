"""
Parent/Guardian Account Management API

This module provides REST API endpoints for managing parent and guardian accounts
in the School Information Management System (SIMS).

Purpose:
    Handles parent/guardian account operations including profile management,
    viewing associated children (students), and account creation.

Features:
    - Parent account creation (admin only)
    - Retrieve all parent accounts (admin only)
    - View own parent profile (authenticated parents)
    - Access list of associated children/students (authenticated parents)

Access Control:
    - Admin endpoints: Require superuser authentication
    - Parent endpoints: Require active user authentication with parent role
    - All endpoints require valid JWT authentication tokens

Routes:
    GET  /api/v1/parents/          - List all parents (admin only)
    POST /api/v1/parents/          - Create new parent (admin only)
    GET  /api/v1/parents/me        - Get current parent profile
    GET  /api/v1/parents/my-children - Get children of current parent
"""

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
    """
    Retrieve all parent accounts with pagination.
    
    This endpoint returns a paginated list of all parent/guardian accounts
    in the system. Only accessible by superuser/admin accounts.
    
    Parameters:
        db (Session): Database session dependency
        skip (int): Number of records to skip for pagination (default: 0)
        limit (int): Maximum number of records to return (default: 100)
        current_user (Any): Currently authenticated superuser
    
    Authentication:
        Requires: Active superuser authentication
        Token: JWT Bearer token in Authorization header
    
    Returns:
        List[Parent]: List of parent account objects with the following fields:
            - id: Unique parent identifier
            - email: Parent's email address
            - name: Parent's full name
            - phone: Contact phone number
            - students: List of associated student IDs
    
    Raises:
        HTTPException:
            - 401 Unauthorized: Missing or invalid authentication token
            - 403 Forbidden: User is not a superuser
    
    HTTP Status Codes:
        200 OK: Successfully retrieved parent list
        401 Unauthorized: Authentication credentials missing or invalid
        403 Forbidden: Insufficient permissions (non-superuser)
    """
    # Retrieve parents from database with pagination
    return crud_parent.get_parents(db, skip=skip, limit=limit)

@router.post("/", response_model=Parent)
def create_parent(
    *,
    db: Session = Depends(deps.get_db),
    parent_in: ParentCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new parent/guardian account.
    
    This endpoint creates a new parent account in the system. Only accessible
    by superuser/admin accounts. Validates that email is unique before creation.
    
    Parameters:
        db (Session): Database session dependency
        parent_in (ParentCreate): Parent creation data from request body
            Required fields:
                - email (str): Unique email address
                - name (str): Full name of parent/guardian
                - password (str): Account password (will be hashed)
            Optional fields:
                - phone (str): Contact phone number
                - address (str): Physical address
        current_user (Any): Currently authenticated superuser
    
    Authentication:
        Requires: Active superuser authentication
        Token: JWT Bearer token in Authorization header
    
    Returns:
        Parent: Newly created parent account object containing:
            - id: Assigned unique identifier
            - email: Parent's email address
            - name: Parent's full name
            - phone: Contact phone number
            - created_at: Account creation timestamp
    
    Raises:
        HTTPException:
            - 400 Bad Request: Parent with email already exists
            - 401 Unauthorized: Missing or invalid authentication token
            - 403 Forbidden: User is not a superuser
            - 422 Unprocessable Entity: Invalid input data format
    
    HTTP Status Codes:
        200 OK: Parent account created successfully
        400 Bad Request: Duplicate email address
        401 Unauthorized: Authentication credentials missing or invalid
        403 Forbidden: Insufficient permissions (non-superuser)
        422 Unprocessable Entity: Validation error in request body
    """
    # Check if parent with this email already exists to prevent duplicates
    parent = crud_parent.get_parent_by_email(db, email=parent_in.email)
    if parent:
        raise HTTPException(status_code=400, detail="Parent already exists")
    
    # Create new parent account with hashed password
    return crud_parent.create_parent(db, parent=parent_in)

@router.get("/me", response_model=Parent)
def read_parent_me(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve current parent's own profile information.
    
    This endpoint returns the profile data for the currently authenticated
    parent/guardian user. Parents can only access their own profile data.
    
    Parameters:
        db (Session): Database session dependency
        current_user (Any): Currently authenticated parent user object
    
    Authentication:
        Requires: Active user authentication (parent role)
        Token: JWT Bearer token in Authorization header
    
    Returns:
        Parent: Current parent's profile object containing:
            - id: Parent's unique identifier
            - email: Parent's email address
            - name: Parent's full name
            - phone: Contact phone number
            - address: Physical address
            - students: List of associated student relationships
    
    Raises:
        HTTPException:
            - 401 Unauthorized: Missing or invalid authentication token
            - 403 Forbidden: User is not an active parent account
    
    HTTP Status Codes:
        200 OK: Successfully retrieved parent profile
        401 Unauthorized: Authentication credentials missing or invalid
        403 Forbidden: User account is inactive or not a parent role
    """
    # Return the authenticated parent's profile directly from current_user context
    # The dependency ensures current_user is the parent object if logged in as parent
    return current_user

@router.get("/my-children", response_model=List[Student])
def read_my_children(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),  # Must be parent
) -> Any:
    """
    Retrieve list of children/students associated with current parent.
    
    This endpoint returns all student records that are linked to the currently
    authenticated parent/guardian account through the parent-student relationship.
    Parents can only view their own children.
    
    Parameters:
        db (Session): Database session dependency
        current_user (Any): Currently authenticated parent user object
    
    Authentication:
        Requires: Active user authentication (parent role)
        Token: JWT Bearer token in Authorization header
    
    Returns:
        List[Student]: List of student objects associated with parent, each containing:
            - id: Student's unique identifier
            - name: Student's full name
            - email: Student's email address
            - grade: Current grade level
            - enrollment_date: Date of enrollment
            - parent_id: Reference to parent account
    
    Raises:
        HTTPException:
            - 401 Unauthorized: Missing or invalid authentication token
            - 403 Forbidden: User is not an active parent account
            - 404 Not Found: Parent account not found in database
    
    HTTP Status Codes:
        200 OK: Successfully retrieved children list (may be empty)
        401 Unauthorized: Authentication credentials missing or invalid
        403 Forbidden: User account is inactive or not a parent role
        404 Not Found: Parent record does not exist
    """
    # Reload parent from database to ensure the relationship collection is properly loaded
    # The ORM relationship 'students' provides access to all children linked to this parent
    # through the parent-student many-to-many or one-to-many relationship table
    parent = crud_parent.get_parent(db, parent_id=current_user.id)
    
    # Verify parent exists in database (defensive check)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    
    # Return the students collection from the parent-student relationship
    # This leverages the ORM relationship defined in the Parent model
    return parent.students
