"""
Classroom Management API Endpoints.

This module provides RESTful API endpoints for managing classrooms in the school
information management system.

Purpose:
    - Classroom lifecycle management (create, read, update, delete)
    - Teacher assignment tracking and filtering
    - Classroom information retrieval and organization

Features:
    - CRUD operations for classroom entities
    - Teacher-based classroom filtering for quick lookups
    - Pagination support for large classroom lists
    - Unique classroom name validation

Access Control:
    - Read operations: Available to all authenticated users
    - Create/Update/Delete: Restricted to administrators only
    - Authentication required for all endpoints via JWT tokens
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_class_room
from app.schemas.class_room import ClassRoom, ClassRoomCreate, ClassRoomUpdate

router = APIRouter()

@router.get("/", response_model=List[ClassRoom])
def read_class_rooms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    teacher_id: Optional[str] = Query(None, description="Filter by Teacher ID"),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve classrooms with optional teacher-based filtering.
    
    Fetch a paginated list of all classrooms in the system. Supports filtering
    by teacher ID to retrieve only classrooms assigned to a specific teacher.
    
    Authentication:
        Requires valid JWT token for any active user.
    
    Args:
        db (Session): Database session dependency injection.
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        teacher_id (str, optional): Filter classrooms by assigned teacher ID.
            If provided, returns only classrooms where this teacher is assigned.
        current_user (Any): Currently authenticated user from JWT token.
    
    Returns:
        List[ClassRoom]: List of classroom objects matching the query criteria.
            Each classroom includes id, name, teacher assignments, and metadata.
    
    Raises:
        HTTPException: 401 if user is not authenticated.
        HTTPException: 403 if user account is inactive.
    
    HTTP Status Codes:
        200: Successfully retrieved classrooms
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User account is inactive
    """
    # Filter by teacher if teacher_id parameter is provided
    if teacher_id:
        return crud_class_room.get_class_rooms_by_teacher(db, teacher_id=teacher_id, skip=skip, limit=limit)
    # Otherwise return all classrooms with pagination
    return crud_class_room.get_class_rooms(db, skip=skip, limit=limit)

@router.post("/", response_model=ClassRoom)
def create_class_room(
    *,
    db: Session = Depends(deps.get_db),
    class_room_in: ClassRoomCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Create a new classroom in the system.
    
    Validates that the classroom name is unique before creation. Only administrators
    are authorized to create new classrooms.
    
    Authentication:
        Requires valid JWT token with superuser/administrator privileges.
    
    Args:
        db (Session): Database session dependency injection.
        class_room_in (ClassRoomCreate): Classroom creation schema containing:
            - name (str): Unique name for the classroom
            - teacher_id (str, optional): ID of assigned teacher
            - capacity (int, optional): Maximum student capacity
            - Additional classroom metadata fields
        current_user (Any): Currently authenticated superuser from JWT token.
    
    Returns:
        ClassRoom: The newly created classroom object with generated ID and timestamps.
    
    Raises:
        HTTPException: 400 if classroom name already exists in the system.
        HTTPException: 401 if user is not authenticated.
        HTTPException: 403 if user is not a superuser/administrator.
    
    HTTP Status Codes:
        200: Classroom created successfully
        400: Bad Request - Classroom name already exists
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User does not have administrator privileges
    """
    class_room = crud_class_room.get_class_room_by_name(db, name=class_room_in.name)
    if class_room:
        raise HTTPException(status_code=400, detail="Class room with this name already exists")
    return crud_class_room.create_class_room(db, class_room=class_room_in)

@router.get("/{class_id}", response_model=ClassRoom)
def read_class_room(
    class_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve a specific classroom by its unique identifier.
    
    Fetches detailed information about a single classroom including all associated
    metadata, teacher assignments, and configuration.
    
    Authentication:
        Requires valid JWT token for any active user.
    
    Args:
        class_id (str): Unique identifier of the classroom to retrieve.
        db (Session): Database session dependency injection.
        current_user (Any): Currently authenticated user from JWT token.
    
    Returns:
        ClassRoom: Complete classroom object including:
            - id: Unique classroom identifier
            - name: Classroom name
            - teacher_id: Assigned teacher (if any)
            - capacity: Maximum student capacity
            - created_at, updated_at: Timestamps
            - Additional classroom metadata
    
    Raises:
        HTTPException: 404 if classroom with the specified ID does not exist.
        HTTPException: 401 if user is not authenticated.
        HTTPException: 403 if user account is inactive.
    
    HTTP Status Codes:
        200: Classroom retrieved successfully
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User account is inactive
        404: Not Found - Classroom does not exist
    """
    class_room = crud_class_room.get_class_room(db, class_room_id=class_id)
    if not class_room:
        raise HTTPException(status_code=404, detail="Class room not found")
    return class_room

@router.put("/{class_id}", response_model=ClassRoom)
def update_class_room(
    *,
    db: Session = Depends(deps.get_db),
    class_id: str,
    class_room_in: ClassRoomUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Update an existing classroom's information.
    
    Modifies classroom details such as name, teacher assignment, capacity, or other
    metadata. Only administrators are authorized to update classrooms.
    
    Authentication:
        Requires valid JWT token with superuser/administrator privileges.
    
    Args:
        db (Session): Database session dependency injection.
        class_id (str): Unique identifier of the classroom to update.
        class_room_in (ClassRoomUpdate): Classroom update schema containing fields to modify:
            - name (str, optional): New classroom name
            - teacher_id (str, optional): New teacher assignment
            - capacity (int, optional): New maximum capacity
            - All fields are optional; only provided fields are updated
        current_user (Any): Currently authenticated superuser from JWT token.
    
    Returns:
        ClassRoom: The updated classroom object with all current values.
    
    Raises:
        HTTPException: 404 if classroom with the specified ID does not exist.
        HTTPException: 401 if user is not authenticated.
        HTTPException: 403 if user is not a superuser/administrator.
    
    HTTP Status Codes:
        200: Classroom updated successfully
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User does not have administrator privileges
        404: Not Found - Classroom does not exist
    """
    class_room = crud_class_room.get_class_room(db, class_room_id=class_id)
    if not class_room:
        raise HTTPException(status_code=404, detail="Class room not found")
    return crud_class_room.update_class_room(db, db_class_room=class_room, class_room_update=class_room_in)

@router.delete("/{class_id}", response_model=ClassRoom)
def delete_class_room(
    *,
    db: Session = Depends(deps.get_db),
    class_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Delete a classroom from the system.
    
    Permanently removes a classroom record. Only administrators are authorized
    to delete classrooms. Returns the deleted classroom data for confirmation.
    
    Authentication:
        Requires valid JWT token with superuser/administrator privileges.
    
    Args:
        db (Session): Database session dependency injection.
        class_id (str): Unique identifier of the classroom to delete.
        current_user (Any): Currently authenticated superuser from JWT token.
    
    Returns:
        ClassRoom: The deleted classroom object with its final state before deletion.
    
    Raises:
        HTTPException: 404 if classroom with the specified ID does not exist.
        HTTPException: 401 if user is not authenticated.
        HTTPException: 403 if user is not a superuser/administrator.
    
    HTTP Status Codes:
        200: Classroom deleted successfully
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User does not have administrator privileges
        404: Not Found - Classroom does not exist
    
    Note:
        Deletion may be restricted if the classroom has associated students or other
        dependencies, depending on database constraints.
    """
    class_room = crud_class_room.get_class_room(db, class_room_id=class_id)
    if not class_room:
        raise HTTPException(status_code=404, detail="Class room not found")
    return crud_class_room.delete_class_room(db, class_room_id=class_id)