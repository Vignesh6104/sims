"""
School Event Management API.

This module provides RESTful API endpoints for managing school events including
announcements, holidays, and school activities. Events are displayed in the school
calendar and can be used to track important dates and information.

Features:
    - Create new school events (announcements, holidays, activities)
    - Retrieve all events with pagination support
    - Delete existing events
    - Calendar integration for event display

Access Control:
    - Event Creation: Requires admin/superuser privileges
    - Event Viewing: Available to all authenticated users
    - Event Deletion: Requires admin/superuser privileges

The module uses FastAPI's dependency injection for database sessions and
authentication/authorization checks.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_event
from app.schemas.event import Event, EventCreate

router = APIRouter()

@router.get("/", response_model=List[Event])
def read_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all school events with pagination.

    This endpoint returns a list of all school events including announcements,
    holidays, and activities. Results are paginated to improve performance.

    Parameters:
        db (Session): Database session dependency
        skip (int): Number of records to skip for pagination (default: 0)
        limit (int): Maximum number of records to return (default: 100)
        current_user (Any): Currently authenticated active user

    Authentication:
        Requires: Valid JWT token for any active user

    Returns:
        List[Event]: List of event objects containing event details

    HTTP Status Codes:
        200: Events retrieved successfully
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User account is not active

    Example:
        GET /api/v1/events?skip=0&limit=50
    """
    return crud_event.get_events(db, skip=skip, limit=limit)

@router.post("/", response_model=Event)
def create_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: EventCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admins
) -> Any:
    """
    Create a new school event.

    This endpoint allows administrators to create new school events such as
    announcements, holidays, or school activities. The event will be visible
    to all users and can be integrated into the school calendar.

    Parameters:
        db (Session): Database session dependency
        event_in (EventCreate): Event data containing title, description, date, type, etc.
        current_user (Any): Currently authenticated superuser/admin

    Authentication:
        Requires: Valid JWT token with superuser/admin privileges

    Returns:
        Event: Created event object with all details including generated ID

    Raises:
        HTTPException: If validation fails or database constraints are violated

    HTTP Status Codes:
        200: Event created successfully
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User does not have admin privileges
        422: Unprocessable Entity - Invalid event data

    Example:
        POST /api/v1/events
        Body: {
            "title": "Spring Break",
            "description": "School holiday",
            "start_date": "2024-03-15",
            "end_date": "2024-03-22",
            "event_type": "holiday"
        }
    """
    return crud_event.create_event(db, event=event_in)

@router.delete("/{event_id}", response_model=Event)
def delete_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a school event by ID.

    This endpoint allows administrators to remove an existing school event
    from the system. The event will no longer appear in the calendar or
    event listings.

    Parameters:
        db (Session): Database session dependency
        event_id (str): Unique identifier of the event to delete
        current_user (Any): Currently authenticated superuser/admin

    Authentication:
        Requires: Valid JWT token with superuser/admin privileges

    Returns:
        Event: Deleted event object with all details

    Raises:
        HTTPException: 
            - 404 if event with given ID does not exist
            - 403 if user lacks admin privileges
            - 401 if authentication is invalid

    HTTP Status Codes:
        200: Event deleted successfully
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User does not have admin privileges
        404: Not Found - Event with specified ID does not exist

    Example:
        DELETE /api/v1/events/123e4567-e89b-12d3-a456-426614174000
    """
    event = crud_event.get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return crud_event.delete_event(db, event_id=event_id)