"""User Notification System API

This module provides RESTful API endpoints for managing user notifications in the
School Information Management System (SIMS).

Purpose:
    Enables real-time and asynchronous communication with users through notifications.
    Supports creating, viewing, and managing notifications across different user roles.

Features:
    - Send notifications: Authorized staff can create and send notifications
    - View notifications: Users can retrieve their role-specific notifications
    - Mark as read: Users can mark individual notifications as read
    - Role-based filtering: Notifications are filtered by user role and recipient

Access Control:
    - GET /: Requires active user authentication (all roles)
    - POST /: Requires active staff authentication (teachers and admins only)
    - PUT /{notification_id}/read: Requires active user authentication (all roles)

Role-Based Notification Delivery:
    Notifications are delivered based on user roles:
    - Admin: Receives system-wide and admin-specific notifications
    - Teacher: Receives teacher-specific and class-related notifications
    - Student: Receives student-specific and academic notifications
    - Parent: Receives parent-specific and child-related notifications
    
    The system automatically detects the user's role by checking the instance type
    of the authenticated user object and filters notifications accordingly.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_notification
from app.schemas.notification import Notification, NotificationCreate

router = APIRouter()

@router.get("/", response_model=List[Notification])
def read_my_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
):
    """Retrieve notifications for the authenticated user.
    
    Fetches all notifications relevant to the current user, filtered by their role.
    Results are paginated and sorted by creation date (newest first).
    
    Parameters:
        db (Session): Database session dependency
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        current_user (Any): Authenticated user object (Admin, Teacher, Student, or Parent)
    
    Authentication:
        Requires valid JWT token for an active user (any role)
    
    Returns:
        List[Notification]: List of notification objects containing:
            - id: Unique notification identifier
            - title: Notification title
            - message: Notification content
            - recipient_role: Target role(s) for the notification
            - recipient_id: Specific user ID (if targeted)
            - is_read: Read status
            - created_at: Timestamp of creation
    
    Raises:
        HTTPException: 401 Unauthorized if authentication fails
        HTTPException: 403 Forbidden if user is inactive
    
    HTTP Status Codes:
        200: Success - Returns list of notifications
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User account is inactive
    """
    # Determine role by checking instance type of the authenticated user object
    # Since user models don't have a unified 'role' field, we infer the role
    # by examining which model class the current_user is an instance of
    from app.models.admin import Admin
    from app.models.teacher import Teacher
    from app.models.student import Student
    from app.models.parent import Parent
    
    # Default to student role if no other role matches
    role = "student"
    # Check instance type to determine user role for notification filtering
    if isinstance(current_user, Admin): 
        role = "admin"
    elif isinstance(current_user, Teacher): 
        role = "teacher"
    elif isinstance(current_user, Parent): 
        role = "parent"
    # Student role is default fallback
    
    # Filter notifications by user ID and role to ensure users only see relevant notifications
    return crud_notification.get_notifications_for_user(db, user_id=current_user.id, role=role, skip=skip, limit=limit)

@router.post("/", response_model=Notification)
def send_notification(
    *,
    db: Session = Depends(deps.get_db),
    notification_in: NotificationCreate,
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """Create and send a notification.
    
    Creates a new notification that can be sent to specific users or roles.
    Only staff members (teachers and admins) are authorized to send notifications.
    
    Parameters:
        db (Session): Database session dependency
        notification_in (NotificationCreate): Notification data containing:
            - title: Notification title (required)
            - message: Notification message content (required)
            - recipient_role: Target role (admin, teacher, student, parent) (optional)
            - recipient_id: Specific user ID for targeted notifications (optional)
        current_user (Any): Authenticated staff user (Teacher or Admin)
    
    Authentication:
        Requires valid JWT token for an active staff member (teacher or admin role only)
    
    Returns:
        Notification: Created notification object with:
            - id: Unique notification identifier
            - title: Notification title
            - message: Notification content
            - recipient_role: Target role
            - recipient_id: Target user ID (if specified)
            - is_read: Read status (defaults to False)
            - created_at: Timestamp of creation
    
    Raises:
        HTTPException: 401 Unauthorized if authentication fails
        HTTPException: 403 Forbidden if user is not staff or is inactive
        HTTPException: 422 Unprocessable Entity if request data is invalid
    
    HTTP Status Codes:
        200: Success - Notification created successfully
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User is not authorized (not staff) or account is inactive
        422: Unprocessable Entity - Invalid request data format
    """
    # Only teachers and admins can send notifications (enforced by get_current_active_staff)
    return crud_notification.create_notification(db, notification=notification_in)

@router.put("/{notification_id}/read", response_model=Notification)
def mark_read(
    notification_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """Mark a notification as read.
    
    Updates the read status of a specific notification to indicate that the user
    has viewed it. This helps users track which notifications are new or unread.
    
    Parameters:
        notification_id (str): Unique identifier of the notification to mark as read
        db (Session): Database session dependency
        current_user (Any): Authenticated user object (any role)
    
    Authentication:
        Requires valid JWT token for an active user (any role)
    
    Returns:
        Notification: Updated notification object with:
            - id: Notification identifier
            - title: Notification title
            - message: Notification content
            - recipient_role: Target role
            - recipient_id: Target user ID
            - is_read: Read status (set to True)
            - created_at: Original creation timestamp
            - read_at: Timestamp when marked as read
    
    Raises:
        HTTPException: 401 Unauthorized if authentication fails
        HTTPException: 403 Forbidden if user is inactive
        HTTPException: 404 Not Found if notification_id doesn't exist
    
    HTTP Status Codes:
        200: Success - Notification marked as read
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - User account is inactive
        404: Not Found - Notification with specified ID not found
    """
    return crud_notification.mark_notification_read(db, notification_id=notification_id)
