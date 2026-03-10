"""
Feedback and Grievance Management API

This module provides endpoints for managing feedback and grievances within the school
information management system.

Purpose:
    - Enable students, teachers, and parents to submit feedback and grievances
    - Provide a centralized system for tracking and responding to feedback
    - Allow administrators to manage, respond to, and update feedback status

Features:
    - Submit new feedback/grievances
    - View submitted feedback (filtered by user role)
    - Admin responses to feedback
    - Status tracking (pending, in_progress, resolved, etc.)
    - Role-based access control

Access Control:
    - Students: Can submit and view their own feedback
    - Teachers: Can submit and view their own feedback
    - Parents: Can submit and view their own feedback
    - Admins: Can view all feedback, respond, and update status
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.feedback import FeedbackStatus
from app.schemas.feedback import Feedback, FeedbackCreate, FeedbackUpdate
from app.crud import crud_feedback

router = APIRouter()

@router.post("/", response_model=Feedback)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Submit new feedback or grievance.
    
    This endpoint allows students, teachers, and parents to submit feedback or
    grievances to the school administration. Admins cannot submit feedback.
    
    Args:
        feedback_in (FeedbackCreate): The feedback data including title, description,
            and category. Required fields are validated in the schema.
        db (Session): Database session dependency injected by FastAPI.
        current_user (Any): Currently authenticated user (Student, Teacher, or Parent).
            Injected via authentication dependency.
    
    Authentication:
        Requires valid JWT token. User must be an active student, teacher, or parent.
    
    Returns:
        Feedback: The created feedback object with assigned ID, timestamps, status,
            and user information.
    
    Raises:
        HTTPException: 
            - 400: If user is not a student, teacher, or parent (e.g., admin attempts)
            - 401: If user is not authenticated (handled by dependency)
            - 422: If validation fails on input data
    
    HTTP Status Codes:
        - 200: Feedback successfully created
        - 400: Invalid user role
        - 401: Unauthorized (not authenticated)
        - 422: Validation error
    
    Example:
        POST /api/v1/feedbacks/
        {
            "title": "Cafeteria food quality",
            "description": "The food quality has declined",
            "category": "facilities"
        }
    """
    # Detect user role by inspecting the class name of the authenticated user
    role = None
    if current_user.__class__.__name__ == "Student":
        role = "student"
    elif current_user.__class__.__name__ == "Teacher":
        role = "teacher"
    elif current_user.__class__.__name__ == "Parent":
        role = "parent"
    
    # Enforce access control: only students, teachers, and parents can submit feedback
    if not role:
         raise HTTPException(status_code=400, detail="Only Students, Teachers, and Parents can submit feedback.")

    return crud_feedback.create_feedback(db=db, feedback=feedback_in, user_id=str(current_user.id), role=role)

@router.get("/", response_model=List[Feedback])
def read_feedbacks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[FeedbackStatus] = None,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve feedback records with role-based filtering.
    
    This endpoint returns feedback based on the user's role:
    - Admins can view all feedback from all users with optional status filtering
    - Students, teachers, and parents can only view their own submitted feedback
    
    Args:
        db (Session): Database session dependency injected by FastAPI.
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        status (FeedbackStatus, optional): Filter by feedback status (pending, 
            in_progress, resolved, etc.). Only applicable for admins. Defaults to None.
        current_user (Any): Currently authenticated user (any role). Injected via
            authentication dependency.
    
    Authentication:
        Requires valid JWT token. User must be active.
    
    Returns:
        List[Feedback]: List of feedback objects. For admins, returns all feedback
            (optionally filtered by status). For other users, returns only their
            own feedback.
    
    Raises:
        HTTPException:
            - 401: If user is not authenticated (handled by dependency)
    
    HTTP Status Codes:
        - 200: Feedback list successfully retrieved
        - 401: Unauthorized (not authenticated)
    
    Example (Admin):
        GET /api/v1/feedbacks/?status=pending&skip=0&limit=10
        Returns: All pending feedback from all users
    
    Example (Student/Teacher/Parent):
        GET /api/v1/feedbacks/
        Returns: Only feedback submitted by the authenticated user
    """
    # Detect user role by examining the class name of the authenticated user
    role = current_user.__class__.__name__
    
    # Admin access control: admins can view all feedback with optional status filter
    if role == "Admin":
        return crud_feedback.get_feedbacks(db, skip=skip, limit=limit, status=status)
    else:
        # Non-admin access control: users can only view their own feedback
        # Map class name to lowercase role string expected by CRUD operations
        role_str = role.lower()
        return crud_feedback.get_user_feedbacks(db, user_id=str(current_user.id), role=role_str, skip=skip, limit=limit)

@router.put("/{feedback_id}", response_model=Feedback)
def update_feedback(
    feedback_id: str,
    feedback_in: FeedbackUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admins - enforced by dependency
) -> Any:
    """
    Update feedback status or add admin response.
    
    This endpoint is restricted to administrators only. It allows admins to:
    - Add responses to submitted feedback
    - Change feedback status (pending -> in_progress -> resolved, etc.)
    - Update any other feedback fields as needed
    
    Args:
        feedback_id (str): UUID of the feedback to update.
        feedback_in (FeedbackUpdate): Updated feedback data. Can include admin_response,
            status, or other modifiable fields. All fields are optional.
        db (Session): Database session dependency injected by FastAPI.
        current_user (Any): Currently authenticated admin user. Access control is
            enforced by get_current_active_superuser dependency.
    
    Authentication:
        Requires valid JWT token with admin/superuser privileges. Only administrators
        can access this endpoint.
    
    Returns:
        Feedback: The updated feedback object with new values and updated timestamp.
    
    Raises:
        HTTPException:
            - 404: If feedback with the given ID is not found
            - 401: If user is not authenticated (handled by dependency)
            - 403: If user is not an admin (handled by dependency)
            - 422: If validation fails on update data
    
    HTTP Status Codes:
        - 200: Feedback successfully updated
        - 401: Unauthorized (not authenticated)
        - 403: Forbidden (not an admin)
        - 404: Feedback not found
        - 422: Validation error
    
    Example:
        PUT /api/v1/feedbacks/123e4567-e89b-12d3-a456-426614174000
        {
            "admin_response": "We will look into this matter",
            "status": "in_progress"
        }
    """
    # Retrieve the feedback record from database
    feedback = crud_feedback.get_feedback(db, feedback_id=feedback_id)
    
    # Verify feedback exists before attempting update
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Apply updates to the feedback record
    feedback = crud_feedback.update_feedback(db=db, db_feedback=feedback, feedback_update=feedback_in)
    return feedback
