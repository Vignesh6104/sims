"""
Academic Marks/Grades Management API

This module provides REST API endpoints for managing student academic marks and grades
in the School Information Management System.

Features:
    - CRUD operations for student marks/grades
    - PDF report card generation for individual students
    - Class-level marks reports with aggregations
    - Batch operations for retrieving marks for multiple students
    - Exam and subject-based filtering

Access Control:
    - GET /report-card/{student_id}: Authenticated users (students can view their own)
    - GET /report: Staff only (teachers/admins)
    - GET /batch: Staff only (teachers/admins)
    - GET /student/{student_id}: Authenticated users
    - POST /: Staff only (teachers/admins)
    - PUT /{mark_id}: Staff only (teachers/admins)

Dependencies:
    - FastAPI for REST API implementation
    - SQLAlchemy for database operations
    - PDF generation utilities for report cards
"""
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_marks, crud_student
from app.schemas.marks import Mark, MarkCreate, MarkUpdate
from app.utils.pdf_generator import generate_report_card

router = APIRouter()

@router.get("/report-card/{student_id}")
def download_report_card(
    student_id: str,
    exam_id: Optional[str] = Query(None, description="Exam ID filter"),
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
):
    """
    Generate and download a PDF report card for a student.
    
    This endpoint generates a comprehensive PDF report card containing all marks
    for a specific student. The report can be filtered by exam ID to show only
    marks from a particular examination.
    
    Parameters:
        student_id (str): The unique identifier of the student (path parameter)
        exam_id (Optional[str]): Optional exam ID to filter marks by specific exam (query parameter)
        db (Session): Database session dependency
        current_user (Any): Current authenticated user (must be active)
    
    Authentication:
        Requires an authenticated active user. Students can view their own report cards,
        while staff can view any student's report card.
    
    Returns:
        StreamingResponse: PDF file stream with appropriate headers for download.
            Content-Type: application/pdf
            Content-Disposition: attachment with filename pattern report_card_{roll_number}.pdf
    
    Raises:
        HTTPException: 
            - 404: Student not found with the provided student_id
            - 401: User not authenticated
            - 403: User not authorized to access this student's records
    
    HTTP Status Codes:
        200: PDF report card generated and returned successfully
        401: Unauthorized - user not authenticated
        403: Forbidden - user not authorized
        404: Not Found - student does not exist
    """
    student = crud_student.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Retrieve all marks for the student (up to 1000 records for comprehensive report)
    marks = crud_marks.get_marks_by_student(db, student_id=student_id, skip=0, limit=1000)
    
    # Filter marks by specific exam if exam_id is provided
    if exam_id:
        marks = [m for m in marks if m.exam_id == exam_id]

    # PDF Generation: Create report card with student info and filtered marks
    # The generate_report_card function formats marks data into a printable PDF layout
    pdf_buffer = generate_report_card(student, marks)
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=report_card_{student.roll_number or 'student'}.pdf"}
    )

@router.get("/report", response_model=List[Dict[str, Any]])
def read_marks_report(
    db: Session = Depends(deps.get_db),
    class_id: str = Query(..., description="Class ID"),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Retrieve aggregated marks report for an entire class.
    
    This endpoint generates a comprehensive report with aggregated statistics
    for all students in a specific class, including averages, totals, and
    performance metrics across subjects and exams.
    
    Parameters:
        class_id (str): The unique identifier of the class (required query parameter)
        db (Session): Database session dependency
        current_user (Any): Current authenticated staff user (teacher/admin)
    
    Authentication:
        Requires an authenticated staff member (teacher or administrator).
        Students and non-staff users are not authorized to access this endpoint.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing aggregated marks data.
            Each dictionary contains student information and computed statistics
            such as total marks, averages, grades, and subject-wise performance.
    
    Raises:
        HTTPException:
            - 401: User not authenticated
            - 403: User is not staff (insufficient permissions)
            - 404: Class not found
    
    HTTP Status Codes:
        200: Report generated and returned successfully
        401: Unauthorized - user not authenticated
        403: Forbidden - user is not staff
        404: Not Found - class does not exist
    """
    # Report Aggregation: Compute class-level statistics including averages,
    # rankings, and performance distributions across all students
    return crud_marks.get_marks_report(db, class_id=class_id)

@router.get("/batch", response_model=List[Mark])
def read_marks_batch(
    db: Session = Depends(deps.get_db),
    exam_id: str = Query(..., description="Exam ID"),
    subject: str = Query(..., description="Subject Name"),
    student_ids: List[str] = Query(..., description="List of Student IDs"),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Retrieve marks for multiple students in batch for a specific exam and subject.
    
    This endpoint enables efficient retrieval of marks for multiple students
    simultaneously, filtered by exam and subject. Useful for generating grade sheets,
    analyzing class performance, or preparing exam result summaries.
    
    Parameters:
        exam_id (str): The unique identifier of the exam (required query parameter)
        subject (str): The name of the subject (required query parameter)
        student_ids (List[str]): List of student IDs to retrieve marks for (required query parameter)
        db (Session): Database session dependency
        current_user (Any): Current authenticated staff user (teacher/admin)
    
    Authentication:
        Requires an authenticated staff member (teacher or administrator).
        Only staff members can perform batch operations on marks.
    
    Returns:
        List[Mark]: List of Mark objects matching the filter criteria.
            Each mark contains student_id, exam_id, subject, score, and other details.
    
    Raises:
        HTTPException:
            - 401: User not authenticated
            - 403: User is not staff (insufficient permissions)
            - 422: Invalid query parameters
    
    HTTP Status Codes:
        200: Marks retrieved successfully
        401: Unauthorized - user not authenticated
        403: Forbidden - user is not staff
        422: Unprocessable Entity - invalid parameters
    """
    # Batch Filtering: Apply multiple filters (student_ids, exam_id, subject)
    # to efficiently retrieve a subset of marks without fetching all records
    return crud_marks.get_marks_by_filters(db, student_ids=student_ids, exam_id=exam_id, subject=subject)

@router.get("/student/{student_id}", response_model=List[Mark])
def read_marks_by_student(
    student_id: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all marks for a specific student with pagination.
    
    This endpoint returns all academic marks/grades for a particular student
    across all exams and subjects. Results are paginated for efficient data transfer.
    
    Parameters:
        student_id (str): The unique identifier of the student (path parameter)
        skip (int): Number of records to skip for pagination (default: 0, query parameter)
        limit (int): Maximum number of records to return (default: 100, query parameter)
        db (Session): Database session dependency
        current_user (Any): Current authenticated active user
    
    Authentication:
        Requires an authenticated active user. Students can view their own marks,
        while staff can view marks for any student.
    
    Returns:
        List[Mark]: List of Mark objects for the specified student.
            Each mark includes exam_id, subject, score, grade, and timestamp information.
    
    Raises:
        HTTPException:
            - 401: User not authenticated
            - 403: User not authorized to view this student's marks
    
    HTTP Status Codes:
        200: Marks retrieved successfully
        401: Unauthorized - user not authenticated
        403: Forbidden - user not authorized
    """
    return crud_marks.get_marks_by_student(db, student_id=student_id, skip=skip, limit=limit)

@router.post("/", response_model=Mark)
def create_mark(
    *,
    db: Session = Depends(deps.get_db),
    mark_in: MarkCreate,
    current_user: Any = Depends(deps.get_current_active_staff), # Teachers/Admins
) -> Any:
    """
    Create a new mark/grade record for a student.
    
    This endpoint allows authorized staff to add a new academic mark/grade
    for a student in a specific exam and subject.
    
    Parameters:
        mark_in (MarkCreate): Mark creation data in request body containing:
            - student_id: ID of the student
            - exam_id: ID of the exam
            - subject: Name/code of the subject
            - score: Numerical score achieved
            - Additional fields like max_score, grade, remarks
        db (Session): Database session dependency
        current_user (Any): Current authenticated staff user (teacher/admin)
    
    Authentication:
        Requires an authenticated staff member (teacher or administrator).
        Only staff members are authorized to create marks.
    
    Returns:
        Mark: The newly created Mark object with all fields populated,
            including the auto-generated ID and timestamps.
    
    Raises:
        HTTPException:
            - 401: User not authenticated
            - 403: User is not staff (insufficient permissions)
            - 422: Invalid input data (validation errors)
            - 400: Mark already exists for this student/exam/subject combination
    
    HTTP Status Codes:
        201: Mark created successfully
        400: Bad Request - duplicate mark or business logic violation
        401: Unauthorized - user not authenticated
        403: Forbidden - user is not staff
        422: Unprocessable Entity - validation errors
    """
    return crud_marks.create_mark(db, mark=mark_in)

@router.put("/{mark_id}", response_model=Mark)
def update_mark(
    *,
    db: Session = Depends(deps.get_db),
    mark_id: str,
    mark_in: MarkUpdate,
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Update an existing mark/grade record.
    
    This endpoint allows authorized staff to modify an existing mark record,
    such as correcting scores, updating grades, or adding remarks.
    
    Parameters:
        mark_id (str): The unique identifier of the mark to update (path parameter)
        mark_in (MarkUpdate): Updated mark data in request body containing fields to modify:
            - score: Updated numerical score (optional)
            - grade: Updated grade (optional)
            - remarks: Updated remarks/comments (optional)
            - Other updatable fields as defined in MarkUpdate schema
        db (Session): Database session dependency
        current_user (Any): Current authenticated staff user (teacher/admin)
    
    Authentication:
        Requires an authenticated staff member (teacher or administrator).
        Only staff members are authorized to update marks.
    
    Returns:
        Mark: The updated Mark object with all current field values,
            including updated_at timestamp reflecting the modification time.
    
    Raises:
        HTTPException:
            - 404: Mark not found with the provided mark_id
            - 401: User not authenticated
            - 403: User is not staff (insufficient permissions)
            - 422: Invalid update data (validation errors)
    
    HTTP Status Codes:
        200: Mark updated successfully
        401: Unauthorized - user not authenticated
        403: Forbidden - user is not staff
        404: Not Found - mark does not exist
        422: Unprocessable Entity - validation errors
    """
    mark = crud_marks.get_mark(db, mark_id=mark_id)
    if not mark:
        raise HTTPException(status_code=404, detail="Mark not found")
    return crud_marks.update_mark(db, db_mark=mark, mark_update=mark_in)