"""
Teacher Management API Endpoints.

This module provides CRUD operations for teacher accounts in the school system.
Teachers are staff members responsible for conducting classes, marking attendance,
grading exams, and managing student assignments.

Access Control:
    - List/Read: Staff members (teachers and admins)
    - Create/Update/Delete: Admins only

Teacher Responsibilities:
    - Conduct classes and manage class rooms
    - Mark student attendance
    - Create and grade assignments
    - Enter exam marks
    - View student performance data
"""
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
    Retrieve list of all teachers with pagination.
    
    Accessible by all staff members (admins and teachers) for viewing
    teacher directory and contact information.
    
    Query Parameters:
        skip (int): Number of records to skip for pagination (default: 0)
        limit (int): Maximum records to return (default: 100, max: 100)
        
    Authentication:
        Requires: Staff role (Admin or Teacher) with valid Bearer token
        
    Returns:
        List[Teacher]: List of teacher profiles with qualification details
        
    HTTP Status Codes:
        200: Successfully retrieved teacher list
        401: Unauthorized (invalid/missing token)
        403: Forbidden (not a staff member)
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
    Create a new teacher profile (Admin only).
    
    Creates a new teacher account with provided credentials and profile data.
    Validates email uniqueness before creation.
    
    Request Body:
        TeacherCreate schema containing:
        - email (str): Unique email address
        - password (str): Plain text password (will be hashed)
        - full_name (str): Teacher's full name
        - qualification (str, optional): Educational background
        - phone (str, optional): Contact number
        - address (str, optional): Residential address
        - subject_specialization (str, optional): Primary subject
        - date_of_joining (date, optional): Employment start date
        
    Authentication:
        Requires: Superuser (Admin) role
        
    Returns:
        Teacher: The newly created teacher object
        
    Raises:
        HTTPException 400: Teacher with email already exists
        
    HTTP Status Codes:
        200: Teacher successfully created
        400: Duplicate email
        401: Unauthorized
        403: Forbidden (not an admin)
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
    Get detailed information for a specific teacher.
    
    Path Parameters:
        teacher_id (str): UUID of the teacher
        
    Authentication:
        Requires: Any authenticated user
        
    Returns:
        Teacher: Teacher's complete profile information
        
    Raises:
        HTTPException 404: Teacher not found
        
    HTTP Status Codes:
        200: Successfully retrieved teacher
        404: Teacher not found
        401: Unauthorized
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
    Update teacher profile information (Admin only).
    
    Allows partial updates - only provided fields will be modified.
    
    Path Parameters:
        teacher_id (str): UUID of the teacher to update
        
    Request Body:
        TeacherUpdate schema (all fields optional):
        - email (str): New email address
        - full_name (str): Updated name
        - password (str): New password
        - qualification (str): Updated qualifications
        - phone (str): New contact number
        - subject_specialization (str): Updated subject
        - is_active (bool): Account status
        
    Authentication:
        Requires: Superuser (Admin) role
        
    Returns:
        Teacher: The updated teacher object
        
    Raises:
        HTTPException 404: Teacher not found
        
    HTTP Status Codes:
        200: Teacher successfully updated
        404: Teacher not found
        401: Unauthorized
        403: Forbidden (not an admin)
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
    Permanently delete a teacher account (Admin only).
    
    Removes the teacher from the system. Note that this may affect
    related data such as class assignments, attendance records, etc.
    
    Path Parameters:
        teacher_id (str): UUID of the teacher to delete
        
    Authentication:
        Requires: Superuser (Admin) role
        
    Returns:
        Teacher: The deleted teacher object (for confirmation)
        
    Raises:
        HTTPException 404: Teacher not found
        
    HTTP Status Codes:
        200: Teacher successfully deleted
        404: Teacher not found
        401: Unauthorized
        403: Forbidden (not an admin)
        
    Warning:
        This operation is permanent. Consider deactivating instead
        by setting is_active=false to preserve historical data.
    """
    teacher = crud_teacher.get_teacher(db, teacher_id=teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher = crud_teacher.delete_teacher(db, teacher_id=teacher_id)
    return teacher
