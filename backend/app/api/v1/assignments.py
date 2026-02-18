"""
Assignment and Submission Management API

This module provides RESTful API endpoints for managing assignments and submissions
in the School Information Management System (SIMS).

Purpose:
    - Enable teachers to create and manage assignments for their classes
    - Allow students to submit assignment files
    - Support grading and feedback workflows
    - Track submission history and grading status

Features:
    - Assignment creation with class association
    - File upload to Cloudinary for submissions (supports multiple file types)
    - Automatic submission tracking with timestamps
    - Grading functionality with grade and feedback
    - Submission history management

Access Control:
    - Teachers (staff): Can create assignments, view all submissions, and grade
    - Students: Can submit assignments and view their own submissions
    - Assignment modification is restricted after grading to maintain integrity
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import shutil
import uuid
from datetime import date
from app.api import deps
from app.crud import crud_assignment
from app.schemas.assignment import Assignment, AssignmentCreate, Submission, SubmissionCreate, SubmissionUpdate
import cloudinary
import cloudinary.uploader
from app.core.config import settings
import tempfile # Import tempfile

router = APIRouter()

@router.get("/class/{class_id}", response_model=List[Assignment])
def read_class_assignments(
    class_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all assignments for a specific class.

    This endpoint returns all assignments associated with a given class ID,
    allowing both teachers and students to view the assignments.

    Parameters:
        class_id (str): The unique identifier of the class
        db (Session): Database session dependency
        current_user (Any): Current authenticated user (student or staff)

    Authentication:
        Requires valid user authentication (student or staff)

    Returns:
        List[Assignment]: List of assignment objects for the specified class
            Each assignment includes:
            - id: Assignment unique identifier
            - title: Assignment title
            - description: Assignment description
            - due_date: Assignment deadline
            - class_id: Associated class identifier
            - teacher_id: Creator teacher identifier

    Raises:
        HTTPException: 401 if user is not authenticated

    HTTP Status Codes:
        200: Successfully retrieved assignments
        401: Unauthorized - user not authenticated
    """
    return crud_assignment.get_assignments_by_class(db, class_id=class_id)

@router.get("/teacher", response_model=List[Assignment])
def read_teacher_assignments(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Retrieve all assignments created by the current teacher.

    This endpoint returns all assignments created by the authenticated teacher,
    allowing them to view and manage their own assignments.

    Parameters:
        db (Session): Database session dependency
        current_user (Any): Current authenticated staff user (teacher)

    Authentication:
        Requires valid staff (teacher) authentication

    Returns:
        List[Assignment]: List of assignment objects created by the teacher
            Each assignment includes all assignment details

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not staff

    HTTP Status Codes:
        200: Successfully retrieved assignments
        401: Unauthorized - user not authenticated
        403: Forbidden - user is not staff
    """
    # Assuming current_user is a Teacher
    return crud_assignment.get_assignments_by_teacher(db, teacher_id=current_user.id)

@router.post("/", response_model=Assignment)
def create_assignment(
    *,
    db: Session = Depends(deps.get_db),
    assignment_in: AssignmentCreate,
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Create a new assignment.

    This endpoint allows teachers to create new assignments for their classes,
    specifying the assignment details including title, description, and due date.

    Parameters:
        db (Session): Database session dependency
        assignment_in (AssignmentCreate): Assignment creation data containing:
            - title: Assignment title
            - description: Assignment description
            - due_date: Assignment deadline
            - class_id: Associated class identifier
            - teacher_id: Creator teacher identifier
        current_user (Any): Current authenticated staff user (teacher)

    Authentication:
        Requires valid staff (teacher) authentication

    Returns:
        Assignment: The newly created assignment object with:
            - id: Generated unique identifier
            - All fields from assignment_in
            - created_at: Timestamp of creation

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not staff
        HTTPException: 422 if validation fails

    HTTP Status Codes:
        200: Successfully created assignment
        401: Unauthorized - user not authenticated
        403: Forbidden - user is not staff
        422: Unprocessable Entity - validation error
    """
    return crud_assignment.create_assignment(db, assignment=assignment_in)

@router.post("/submissions", response_model=Submission)
async def submit_assignment(
    *,
    db: Session = Depends(deps.get_db),
    assignment_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Submit an assignment file.

    This endpoint allows students to upload their assignment submissions. The file
    is uploaded to Cloudinary for secure storage. Students can resubmit if the
    assignment hasn't been graded yet.

    Parameters:
        db (Session): Database session dependency
        assignment_id (str): The unique identifier of the assignment being submitted
        file (UploadFile): The file being uploaded (supports multiple formats)
        current_user (Any): Current authenticated user (student)

    Authentication:
        Requires valid user authentication (student)

    Returns:
        Submission: The submission object containing:
            - id: Submission unique identifier
            - assignment_id: Associated assignment identifier
            - student_id: Submitting student identifier
            - content: Cloudinary URL of uploaded file
            - submission_date: Date of submission
            - grade: Grade value (null if not graded)
            - feedback: Teacher feedback (null if not graded)

    Raises:
        HTTPException: 400 if assignment already graded (cannot edit)
        HTTPException: 401 if user is not authenticated
        HTTPException: 500 if Cloudinary upload fails

    HTTP Status Codes:
        200: Successfully submitted assignment
        400: Bad Request - assignment already graded
        401: Unauthorized - user not authenticated
        500: Internal Server Error - file upload failed
    """
    # Check if student has already submitted this assignment
    existing = crud_assignment.get_submission_by_student(db, assignment_id=assignment_id, student_id=current_user.id)
    
    # Prevent editing submissions that have already been graded to maintain integrity
    if existing and existing.grade is not None:
        raise HTTPException(status_code=400, detail="Assignment already graded and cannot be edited")
    
    # Upload file to Cloudinary cloud storage for persistent and accessible file hosting
    temp_file_path = None
    try:
        # Create a named temporary file to store the uploaded file before Cloudinary upload
        # This is necessary because Cloudinary's upload method requires a file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # Copy the uploaded file content to the temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name # Get the path of the temporary file
            
        # Upload the temporary file to Cloudinary with automatic resource type detection
        upload_result = cloudinary.uploader.upload(
            temp_file_path, 
            folder="sims_assignments",  # Organize uploads in dedicated folder
            resource_type="auto"  # Auto-detect file type (image, video, document, etc.)
        )
        # Extract the secure URL from Cloudinary response
        file_url = upload_result.get("secure_url") or upload_result.get("url")
        if not file_url:
            raise HTTPException(status_code=500, detail="Cloudinary upload failed: No URL returned")
        
        file_url = str(file_url) # Ensure it's a string
            
    except cloudinary.exceptions.Error as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload processing failed: {e}")
    finally:
        # Clean up: Always remove the temporary file to prevent disk space accumulation
        # This runs regardless of upload success or failure
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path) # Clean up the temporary file

    if existing:
        # Update existing submission with new file URL and submission date
        # Optionally, delete old file from Cloudinary here if needed, requires public_id
        
        existing.content = file_url
        existing.submission_date = date.today()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new submission record in the database
    submission_in = SubmissionCreate(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=file_url,
        submission_date=date.today()
    )
    
    return crud_assignment.create_submission(db, submission=submission_in)

@router.get("/submissions/{assignment_id}", response_model=List[Submission])
def read_submissions(
    assignment_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Retrieve all submissions for a specific assignment.

    This endpoint allows teachers to view all student submissions for a given
    assignment, including graded and ungraded submissions.

    Parameters:
        assignment_id (str): The unique identifier of the assignment
        db (Session): Database session dependency
        current_user (Any): Current authenticated staff user (teacher)

    Authentication:
        Requires valid staff (teacher) authentication

    Returns:
        List[Submission]: List of submission objects for the assignment
            Each submission includes:
            - id: Submission unique identifier
            - assignment_id: Associated assignment identifier
            - student_id: Submitting student identifier
            - content: URL to submitted file on Cloudinary
            - submission_date: Date of submission
            - grade: Grade value (null if not graded)
            - feedback: Teacher feedback (null if not graded)

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not staff

    HTTP Status Codes:
        200: Successfully retrieved submissions
        401: Unauthorized - user not authenticated
        403: Forbidden - user is not staff
    """
    return crud_assignment.get_submissions_by_assignment(db, assignment_id=assignment_id)

@router.get("/my-submissions", response_model=List[Submission])
def read_my_submissions(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all submissions for the current student.

    This endpoint allows students to view all their assignment submissions,
    including submission status, grades, and feedback.

    Parameters:
        db (Session): Database session dependency
        current_user (Any): Current authenticated user (student)

    Authentication:
        Requires valid user authentication (student)

    Returns:
        List[Submission]: List of all submission objects for the student
            Each submission includes:
            - id: Submission unique identifier
            - assignment_id: Associated assignment identifier
            - student_id: Student identifier (current user)
            - content: URL to submitted file on Cloudinary
            - submission_date: Date of submission
            - grade: Grade value (null if not graded)
            - feedback: Teacher feedback (null if not graded)

    Raises:
        HTTPException: 401 if user is not authenticated

    HTTP Status Codes:
        200: Successfully retrieved submissions
        401: Unauthorized - user not authenticated
    """
    return crud_assignment.get_all_submissions_by_student(db, student_id=current_user.id)

@router.put("/submissions/{submission_id}", response_model=Submission)
def grade_submission(
    submission_id: str,
    submission_in: SubmissionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Grade a student submission.

    This endpoint allows teachers to assign a grade and provide feedback for
    a student's assignment submission. Once graded, students cannot edit their
    submission to maintain academic integrity.

    Parameters:
        submission_id (str): The unique identifier of the submission to grade
        submission_in (SubmissionUpdate): Grading data containing:
            - grade: Numeric grade value
            - feedback: Optional text feedback for the student
        db (Session): Database session dependency
        current_user (Any): Current authenticated staff user (teacher)

    Authentication:
        Requires valid staff (teacher) authentication

    Returns:
        Submission: The updated submission object with:
            - id: Submission unique identifier
            - assignment_id: Associated assignment identifier
            - student_id: Submitting student identifier
            - content: URL to submitted file
            - submission_date: Original submission date
            - grade: Updated grade value
            - feedback: Updated feedback text

    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not staff
        HTTPException: 404 if submission not found

    HTTP Status Codes:
        200: Successfully graded submission
        401: Unauthorized - user not authenticated
        403: Forbidden - user is not staff
        404: Not Found - submission does not exist
    """
    # Need to fetch the submission first... simplified:
    # We don't have get_submission_by_id in crud yet, adding direct query here for speed
    from app.models.assignment import Submission as SubmissionModel
    db_sub = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return crud_assignment.update_submission(db, db_submission=db_sub, submission_update=submission_in)
