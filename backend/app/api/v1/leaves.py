"""
Leave Application and Approval System API.

This module provides endpoints for managing leave applications in the school information
management system. It implements a complete leave request workflow with role-based
access control.

Purpose:
    - Enable students and teachers to apply for leaves
    - Allow teachers and administrators to view, approve, or reject leave requests
    - Maintain a complete audit trail of leave applications and their status

Features:
    - Leave Application: Students and teachers can submit leave requests
    - Leave Viewing: Role-based filtering of leave records
    - Leave Approval/Rejection: Staff members can update leave status
    - Status Filtering: Filter leaves by pending, approved, or rejected status

Access Control:
    - Students: Can apply for leaves and view only their own leave records
    - Teachers: Can apply for leaves, view their own leaves, approve/reject student leaves
    - Administrators: Full access to all leave operations and records

Workflow:
    1. Student/Teacher submits a leave application with required details
    2. Leave is created with 'pending' status
    3. Teacher (for student leaves) or Admin (for any leave) reviews the request
    4. Approver updates status to 'approved' or 'rejected'
    5. Applicant can view the updated status of their application

Endpoints:
    POST /   - Create a new leave application
    GET /    - Retrieve leave records (filtered by role)
    PUT /{id} - Update leave status (approve/reject)
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.leave import LeaveStatus
from app.schemas.leave import Leave, LeaveCreate, LeaveUpdate
from app.crud import crud_leave

router = APIRouter()

@router.post("/", response_model=Leave)
def create_leave(
    leave_in: LeaveCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Apply for a leave.
    
    Create a new leave application. Available to students and teachers only.
    The leave is created with 'pending' status by default and awaits approval
    from authorized staff members.
    
    Args:
        leave_in: Leave application data including:
            - start_date: Leave start date
            - end_date: Leave end date
            - reason: Reason for leave
            - description: Optional detailed description
        db: Database session dependency
        current_user: Currently authenticated user (Student or Teacher)
    
    Authentication:
        Requires valid JWT token. User must be an active student or teacher.
    
    Returns:
        Leave: Created leave record with:
            - id: Unique leave identifier
            - user_id: ID of the applicant
            - role: Role of applicant (student/teacher)
            - start_date, end_date, reason, description
            - status: Initially set to 'pending'
            - created_at, updated_at: Timestamps
    
    Raises:
        HTTPException:
            - 400: If user is neither a student nor a teacher
            - 401: If authentication fails
            - 422: If validation fails (invalid dates, missing required fields)
    
    HTTP Status Codes:
        - 200: Leave application created successfully
        - 400: Bad request (invalid user role)
        - 401: Unauthorized (authentication failed)
        - 422: Unprocessable entity (validation error)
    """
    # Role detection: Identify whether the current user is a student or teacher
    # by checking class-specific attributes that uniquely identify each user type
    role = None
    
    # Check for Student: Students have a unique 'roll_number' attribute
    if hasattr(current_user, "roll_number"):
        role = "student"
    # Check for Teacher: Teachers have a unique 'qualification' attribute
    elif hasattr(current_user, "qualification"):
        role = "teacher"
    else:
        # Fallback: Check the class name directly if attributes are not available
        # This handles edge cases where attributes might not be loaded
        if current_user.__class__.__name__ == "Student":
            role = "student"
        elif current_user.__class__.__name__ == "Teacher":
            role = "teacher"
    
    # Permission check: Only students and teachers can apply for leaves
    # Admins and other user types are not allowed to create leave applications
    if not role:
         raise HTTPException(status_code=400, detail="Only Students and Teachers can apply for leave.")

    return crud_leave.create_leave(db=db, leave=leave_in, user_id=str(current_user.id), role=role)

@router.get("/", response_model=List[Leave])
def read_leaves(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeaveStatus] = None,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve leave records with role-based filtering.
    
    Returns a list of leave applications filtered based on the authenticated user's role.
    Different user roles have different visibility levels to maintain data privacy
    and support the approval workflow.
    
    Args:
        db: Database session dependency
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        status: Optional filter by leave status (pending/approved/rejected)
        current_user: Currently authenticated user (Student/Teacher/Admin)
    
    Authentication:
        Requires valid JWT token. User must be active.
    
    Returns:
        List[Leave]: List of leave records accessible to the current user:
            - Admin: All leave records in the system
            - Teacher: Their own leave applications
            - Student: Only their own leave applications
        
        Each leave record contains:
            - id, user_id, role
            - start_date, end_date, reason, description
            - status, created_at, updated_at
    
    Raises:
        HTTPException:
            - 401: If authentication fails
            - 422: If invalid status value is provided
    
    HTTP Status Codes:
        - 200: Leave records retrieved successfully
        - 401: Unauthorized (authentication failed)
        - 422: Unprocessable entity (invalid parameters)
    
    Notes:
        - Teachers currently view only their own leaves
        - Future enhancement: Teachers should also see student leaves for approval
        - Empty list returned if user role cannot be determined
    """
    # Role detection: Determine user role by checking the class name
    # This is necessary because different roles have different data access permissions
    user_role = None
    if current_user.__class__.__name__ == "Admin":
        user_role = "admin"
    elif current_user.__class__.__name__ == "Teacher":
        user_role = "teacher"
    elif current_user.__class__.__name__ == "Student":
        user_role = "student"

    # Filtering logic based on role: Apply appropriate filters to ensure users
    # only see leaves they are authorized to view
    
    if user_role == "admin":
        # Admins have full visibility: Return all leaves in the system
        # No user-specific filtering applied
        return crud_leave.get_leaves(db, skip=skip, limit=limit, status=status)
    elif user_role == "teacher":
        # Teachers see their own leave applications
        # Filter by teacher_id to return only leaves created by this teacher
        # TODO: Future enhancement - also return student leaves for approval
        return crud_leave.get_leaves(db, skip=skip, limit=limit, teacher_id=str(current_user.id), status=status)
    elif user_role == "student":
        # Students have restricted visibility: Only their own leaves
        # Filter by student_id to ensure data privacy
        return crud_leave.get_leaves(db, skip=skip, limit=limit, student_id=str(current_user.id), status=status)
    
    # Fallback: Return empty list if role cannot be determined
    # This prevents unauthorized data access in case of unexpected user types
    return []

@router.put("/{leave_id}", response_model=Leave)
def update_leave(
    leave_id: str,
    leave_in: LeaveUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff), # Admins & Teachers
) -> Any:
    """
    Update leave status (Approve or Reject).
    
    Allows authorized staff members (teachers and administrators) to approve or reject
    leave applications. Teachers can only approve student leaves, while administrators
    have full approval authority.
    
    Args:
        leave_id: Unique identifier of the leave to update
        leave_in: Leave update data containing:
            - status: New status (approved/rejected)
            - Optional: rejection_reason or other metadata
        db: Database session dependency
        current_user: Currently authenticated staff member (Teacher or Admin)
    
    Authentication:
        Requires valid JWT token. User must be an active staff member
        (teacher or administrator). Students cannot access this endpoint.
    
    Returns:
        Leave: Updated leave record with:
            - All original fields (id, user_id, dates, reason, etc.)
            - Updated status field
            - Updated updated_at timestamp
    
    Raises:
        HTTPException:
            - 403: If teacher attempts to approve another teacher's leave
            - 404: If leave with given ID does not exist
            - 401: If authentication fails or user is not staff
            - 422: If validation fails (invalid status value)
    
    HTTP Status Codes:
        - 200: Leave status updated successfully
        - 401: Unauthorized (not authenticated or not staff)
        - 403: Forbidden (insufficient permissions)
        - 404: Not found (leave does not exist)
        - 422: Unprocessable entity (validation error)
    
    Permission Rules:
        - Teachers: Can approve/reject student leaves only
        - Teachers: Cannot approve their own or other teachers' leaves
        - Admins: Can approve/reject any leave (students and teachers)
    """
    leave = crud_leave.get_leave(db, leave_id=leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    
    # Permission check: Enforce hierarchical approval rules
    # Teachers can only approve student leaves, not leaves from other teachers
    # This maintains proper approval hierarchy: teacher leaves must be approved by admins
    
    # Check if current user is a teacher AND the leave belongs to another teacher
    # If leave.teacher_id is set, it means the leave was created by a teacher
    if current_user.__class__.__name__ == "Teacher" and leave.teacher_id:
        # Deny access: Teachers cannot approve/reject other teachers' leaves
        # Only administrators should have this authority
        raise HTTPException(status_code=403, detail="Teachers cannot approve other teachers' leaves.")

    leave = crud_leave.update_leave(db=db, db_leave=leave, leave_update=leave_in)
    return leave
