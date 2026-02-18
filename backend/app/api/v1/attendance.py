"""
Student Attendance Tracking API Module.

This module provides RESTful API endpoints for managing student attendance records
in the School Information Management System (SIMS).

Purpose:
    - Track daily student attendance (present/absent/late/excused)
    - Maintain historical attendance records
    - Generate attendance reports and analytics

Features:
    - Mark student attendance for specific dates and classes
    - Retrieve individual student attendance history
    - Generate aggregated attendance reports by class
    - Filter attendance records by student and date range

Access Control:
    - Attendance marking: Requires staff role (teachers/administrators)
    - Attendance viewing: Requires authenticated user (staff or students can view own)
    - Reports: Requires staff role for class-level reports

Endpoints:
    POST /: Create a new attendance record
    GET /: Retrieve attendance records with optional filtering
    GET /report: Generate aggregated attendance report for a class
"""
from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_attendance
from app.schemas.attendance import Attendance, AttendanceCreate, AttendanceUpdate

router = APIRouter()

@router.get("/report", response_model=List[Dict[str, Any]])
def read_attendance_report(
    db: Session = Depends(deps.get_db),
    class_id: str = Query(..., description="Class ID"),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Generate aggregated attendance report for a specific class.
    
    This endpoint produces a comprehensive attendance summary for all students
    in the specified class, including statistics such as total days, present days,
    absent days, and attendance percentage.
    
    Args:
        db (Session): Database session dependency injected by FastAPI.
        class_id (str): Unique identifier of the class for which to generate
            the attendance report. Required query parameter.
        current_user (Any): Currently authenticated user with staff role.
            Automatically injected by the authentication dependency.
    
    Authentication:
        Requires: Active staff user (teacher or administrator)
        Dependency: deps.get_current_active_staff
    
    Returns:
        List[Dict[str, Any]]: List of attendance summary dictionaries, one per student.
            Each dictionary contains:
            - student_id: Student's unique identifier
            - student_name: Student's full name
            - total_days: Total number of attendance records
            - present_days: Number of days marked present
            - absent_days: Number of days marked absent
            - late_days: Number of days marked late (if applicable)
            - attendance_percentage: Calculated attendance rate
    
    Raises:
        HTTPException: 401 Unauthorized if user is not authenticated
        HTTPException: 403 Forbidden if user does not have staff role
        HTTPException: 404 Not Found if class_id does not exist
    
    HTTP Status Codes:
        200: Successful report generation
        401: Unauthorized - Invalid or missing authentication
        403: Forbidden - User lacks required staff permissions
        404: Not Found - Class ID does not exist
    
    Example:
        GET /api/v1/attendance/report?class_id=class123
    """
    # Generate aggregated attendance report for the specified class
    # This calls the CRUD layer to compute attendance statistics
    return crud_attendance.get_attendance_report(db, class_id=class_id)

@router.get("/", response_model=List[Attendance])
def read_attendance(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    student_id: str = None,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve attendance records with optional filtering and pagination.
    
    This endpoint allows authenticated users to retrieve attendance records.
    When a student_id is provided, it returns that student's attendance history.
    Without a student_id, it returns an empty list (requires specific filtering).
    
    Args:
        db (Session): Database session dependency injected by FastAPI.
        skip (int, optional): Number of records to skip for pagination.
            Defaults to 0. Use with limit for pagination.
        limit (int, optional): Maximum number of records to return.
            Defaults to 100. Maximum recommended value is 1000.
        student_id (str, optional): Filter attendance records by student ID.
            If provided, returns only records for the specified student.
            If None, returns empty list.
        current_user (Any): Currently authenticated user (staff or student).
            Automatically injected by the authentication dependency.
    
    Authentication:
        Requires: Active authenticated user (staff or student)
        Dependency: deps.get_current_active_user
        Note: Students should only be able to view their own records
              (enforcement may be in permission layer)
    
    Returns:
        List[Attendance]: List of attendance record objects matching the filters.
            Each object contains:
            - id: Unique attendance record identifier
            - student_id: ID of the student
            - date: Date of the attendance record
            - status: Attendance status (present/absent/late/excused)
            - class_id: Associated class identifier
            - remarks: Optional notes about the attendance
            Returns empty list if no student_id is provided.
    
    Raises:
        HTTPException: 401 Unauthorized if user is not authenticated
        HTTPException: 404 Not Found if student_id does not exist
        HTTPException: 422 Validation Error if parameters are invalid
    
    HTTP Status Codes:
        200: Successful retrieval of attendance records
        401: Unauthorized - Invalid or missing authentication
        404: Not Found - Student ID does not exist
        422: Unprocessable Entity - Invalid query parameters
    
    Example:
        GET /api/v1/attendance/?student_id=student123&skip=0&limit=50
    """
    # Filter attendance records by student ID if provided
    if student_id:
        # Retrieve paginated attendance records for the specified student
        # skip and limit parameters enable pagination for large result sets
        attendance = crud_attendance.get_attendance_by_student(db, student_id=student_id, skip=skip, limit=limit)
    else:
        # Return empty list when no student_id filter is provided
        # This prevents returning all attendance records which could be a large dataset
        attendance = []
    return attendance

@router.post("/", response_model=Attendance)
def create_attendance(
    *,
    db: Session = Depends(deps.get_db),
    attendance_in: AttendanceCreate,
    current_user: Any = Depends(deps.get_current_active_staff),  # Only teachers/admins can mark attendance
) -> Any:
    """
    Create a new attendance record for a student.
    
    This endpoint allows staff members (teachers and administrators) to mark
    student attendance for a specific date and class. It creates a new attendance
    record in the database with the provided status and optional remarks.
    
    Args:
        db (Session): Database session dependency injected by FastAPI.
        attendance_in (AttendanceCreate): Request body containing attendance data.
            Required fields:
            - student_id (str): ID of the student being marked
            - date (date): Date for the attendance record
            - status (str): Attendance status (present/absent/late/excused)
            - class_id (str): ID of the class session
            Optional fields:
            - remarks (str): Additional notes about the attendance
        current_user (Any): Currently authenticated user with staff role.
            Automatically injected by the authentication dependency.
            Must be a teacher or administrator to mark attendance.
    
    Authentication:
        Requires: Active staff user (teacher or administrator)
        Dependency: deps.get_current_active_staff
        Restriction: Only staff members can create attendance records
    
    Returns:
        Attendance: The newly created attendance record object containing:
            - id: Unique identifier for the attendance record
            - student_id: ID of the student
            - date: Date of attendance
            - status: Attendance status
            - class_id: Associated class ID
            - remarks: Optional remarks
            - created_at: Timestamp of record creation
            - updated_at: Timestamp of last update
    
    Raises:
        HTTPException: 401 Unauthorized if user is not authenticated
        HTTPException: 403 Forbidden if user does not have staff role
        HTTPException: 404 Not Found if student_id or class_id does not exist
        HTTPException: 422 Validation Error if required fields are missing or invalid
        HTTPException: 409 Conflict if attendance record already exists for this student/date/class
    
    HTTP Status Codes:
        200: Successful creation of attendance record
        401: Unauthorized - Invalid or missing authentication
        403: Forbidden - User lacks required staff permissions
        404: Not Found - Student or class does not exist
        409: Conflict - Duplicate attendance record
        422: Unprocessable Entity - Invalid request data
    
    Example:
        POST /api/v1/attendance/
        Body: {
            "student_id": "student123",
            "date": "2024-01-15",
            "status": "present",
            "class_id": "class456",
            "remarks": "On time"
        }
    """
    # Create and persist the new attendance record in the database
    # The CRUD layer handles validation and database operations
    return crud_attendance.create_attendance(db, attendance=attendance_in)
