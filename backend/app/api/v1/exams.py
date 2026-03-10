"""
Exam/Test Management API Endpoints.

This module provides RESTful API endpoints for managing exams and tests in the
School Information Management System (SIMS).

Features:
    - CRUD operations for exams (Create, Read, Update, Delete)
    - Exam schedule management
    - List exams with pagination support
    - Retrieve individual exam details

Access Control:
    - Read operations: Require active authenticated user
    - Write operations (Create, Update, Delete): Require active staff user
    - All endpoints require valid authentication tokens
"""
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
    Retrieve a list of exams with pagination support.

    This endpoint returns a paginated list of all exams in the system.
    
    Parameters:
        db (Session): Database session dependency
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        current_user (Any): Current authenticated active user from JWT token

    Authentication:
        Requires valid JWT token for an active user.

    Returns:
        List[Exam]: List of exam objects matching the pagination parameters

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not active

    HTTP Status Codes:
        200: Successfully retrieved exam list
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User account is not active
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
    Create a new exam in the system.

    This endpoint allows staff members to create new exams with scheduling
    and configuration details.

    Parameters:
        db (Session): Database session dependency
        exam_in (ExamCreate): Exam creation data including exam details,
            schedule, subject, and other configuration parameters
        current_user (Any): Current authenticated active staff user from JWT token

    Authentication:
        Requires valid JWT token for an active staff user.
        Regular users cannot create exams.

    Returns:
        Exam: The newly created exam object with assigned ID and timestamps

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not an active staff member
        HTTPException: 422 if validation fails for the exam data

    HTTP Status Codes:
        200: Successfully created exam
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User is not staff or not active
        422: Unprocessable Entity - Invalid exam data
    """
    return crud_exam.create_exam(db, exam=exam_in)

@router.get("/{exam_id}", response_model=Exam)
def read_exam(
    exam_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve a specific exam by its unique identifier.

    This endpoint returns detailed information about a single exam including
    its schedule, subject, and configuration details.

    Parameters:
        exam_id (str): Unique identifier of the exam to retrieve
        db (Session): Database session dependency
        current_user (Any): Current authenticated active user from JWT token

    Authentication:
        Requires valid JWT token for an active user.

    Returns:
        Exam: The exam object with all details

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not active
        HTTPException: 404 if exam with the given ID does not exist

    HTTP Status Codes:
        200: Successfully retrieved exam
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User account is not active
        404: Not Found - Exam does not exist
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
    Update an existing exam's details.

    This endpoint allows staff members to modify exam information including
    schedule, subject, and configuration details. Only provided fields will
    be updated.

    Parameters:
        db (Session): Database session dependency
        exam_id (str): Unique identifier of the exam to update
        exam_in (ExamUpdate): Partial or complete exam data to update.
            Only provided fields will be modified.
        current_user (Any): Current authenticated active staff user from JWT token

    Authentication:
        Requires valid JWT token for an active staff user.
        Regular users cannot update exams.

    Returns:
        Exam: The updated exam object with modified fields

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not an active staff member
        HTTPException: 404 if exam with the given ID does not exist
        HTTPException: 422 if validation fails for the updated data

    HTTP Status Codes:
        200: Successfully updated exam
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User is not staff or not active
        404: Not Found - Exam does not exist
        422: Unprocessable Entity - Invalid exam data
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
    Delete an exam from the system.

    This endpoint allows staff members to remove an exam. The deleted exam
    data is returned in the response for reference or audit purposes.

    Parameters:
        db (Session): Database session dependency
        exam_id (str): Unique identifier of the exam to delete
        current_user (Any): Current authenticated active staff user from JWT token

    Authentication:
        Requires valid JWT token for an active staff user.
        Regular users cannot delete exams.

    Returns:
        Exam: The deleted exam object for reference

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not an active staff member
        HTTPException: 404 if exam with the given ID does not exist

    HTTP Status Codes:
        200: Successfully deleted exam
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User is not staff or not active
        404: Not Found - Exam does not exist
    """
    exam = crud_exam.get_exam(db, exam_id=exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return crud_exam.delete_exam(db, exam_id=exam_id)
