"""
Subject/Course Management API Module.

This module provides REST API endpoints for managing subjects (courses) in the
School Information Management System (SIMS).

Features:
    - CRUD operations for subjects
    - Pagination support for listing subjects
    - Subject name uniqueness validation
    - Role-based access control

Access Control:
    - Read operations: Available to all active authenticated users
    - Write operations (Create/Update/Delete): Restricted to active staff members only

Endpoints:
    GET    /            - List all subjects (paginated)
    POST   /            - Create a new subject (staff only)
    GET    /{subject_id} - Retrieve a specific subject
    PUT    /{subject_id} - Update a subject (staff only)
    DELETE /{subject_id} - Delete a subject (staff only)
"""
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
    Retrieve a paginated list of subjects.

    This endpoint returns a list of all subjects in the system with support for
    pagination to handle large datasets efficiently.

    Parameters:
        db (Session): Database session dependency.
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        current_user (Any): Currently authenticated active user.

    Authentication:
        Requires authentication as an active user.

    Returns:
        List[Subject]: A list of subject objects, each containing subject details
        such as id, name, description, and other subject attributes.

    HTTP Status Codes:
        200 OK: Successfully retrieved the list of subjects.
        401 Unauthorized: User is not authenticated.
        403 Forbidden: User is not an active user.

    Example:
        GET /api/v1/subjects/?skip=0&limit=10
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
    Create a new subject in the system.

    This endpoint allows authorized staff members to create new subjects.
    Subject names must be unique across the system.

    Parameters:
        db (Session): Database session dependency.
        subject_in (SubjectCreate): Subject creation data containing name and other
            required subject attributes.
        current_user (Any): Currently authenticated active staff member.

    Authentication:
        Requires authentication as an active staff member (teachers/administrators).

    Returns:
        Subject: The newly created subject object with all its attributes including
        the generated subject ID.

    Raises:
        HTTPException: 400 Bad Request if a subject with the same name already exists.

    HTTP Status Codes:
        201 Created: Subject successfully created.
        400 Bad Request: Subject with this name already exists.
        401 Unauthorized: User is not authenticated.
        403 Forbidden: User is not an active staff member.
        422 Unprocessable Entity: Invalid input data.

    Example:
        POST /api/v1/subjects/
        Body: {"name": "Mathematics", "description": "Core math subject"}
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
    Retrieve a specific subject by its unique identifier.

    This endpoint returns detailed information about a single subject identified
    by its subject_id.

    Parameters:
        subject_id (str): Unique identifier of the subject to retrieve.
        db (Session): Database session dependency.
        current_user (Any): Currently authenticated active user.

    Authentication:
        Requires authentication as an active user.

    Returns:
        Subject: The subject object containing all subject details including id,
        name, description, and other attributes.

    Raises:
        HTTPException: 404 Not Found if the subject does not exist.

    HTTP Status Codes:
        200 OK: Successfully retrieved the subject.
        401 Unauthorized: User is not authenticated.
        403 Forbidden: User is not an active user.
        404 Not Found: Subject with the specified ID does not exist.

    Example:
        GET /api/v1/subjects/SUB-12345
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
    Update an existing subject's information.

    This endpoint allows authorized staff members to modify subject details.
    Only the fields provided in the request body will be updated.

    Parameters:
        db (Session): Database session dependency.
        subject_id (str): Unique identifier of the subject to update.
        subject_in (SubjectUpdate): Subject update data containing the fields to be
            modified (partial updates are supported).
        current_user (Any): Currently authenticated active staff member.

    Authentication:
        Requires authentication as an active staff member (teachers/administrators).

    Returns:
        Subject: The updated subject object with all current attributes.

    Raises:
        HTTPException: 404 Not Found if the subject does not exist.

    HTTP Status Codes:
        200 OK: Subject successfully updated.
        401 Unauthorized: User is not authenticated.
        403 Forbidden: User is not an active staff member.
        404 Not Found: Subject with the specified ID does not exist.
        422 Unprocessable Entity: Invalid input data.

    Example:
        PUT /api/v1/subjects/SUB-12345
        Body: {"description": "Updated description"}
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
    Delete a subject from the system.

    This endpoint allows authorized staff members to permanently remove a subject.
    The deleted subject's data is returned in the response.

    Parameters:
        db (Session): Database session dependency.
        subject_id (str): Unique identifier of the subject to delete.
        current_user (Any): Currently authenticated active staff member.

    Authentication:
        Requires authentication as an active staff member (teachers/administrators).

    Returns:
        Subject: The deleted subject object with all its attributes before deletion.

    Raises:
        HTTPException: 404 Not Found if the subject does not exist.

    HTTP Status Codes:
        200 OK: Subject successfully deleted.
        401 Unauthorized: User is not authenticated.
        403 Forbidden: User is not an active staff member.
        404 Not Found: Subject with the specified ID does not exist.

    Example:
        DELETE /api/v1/subjects/SUB-12345

    Note:
        This operation is permanent. Consider the impact on related records
        (enrollments, grades, etc.) before deleting a subject.
    """
    subject = crud_subject.get_subject(db, subject_id=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud_subject.delete_subject(db, subject_id=subject_id)
