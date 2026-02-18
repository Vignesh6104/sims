"""Quiz Management API Endpoints.

This module provides RESTful API endpoints for quiz management and submission
in the School Information Management System (SIMS).

Purpose:
    Handles quiz creation, retrieval, and student quiz result submissions.

Features:
    - Create quizzes: Teachers and staff can create new quizzes for classes
    - View quizzes: Authenticated users can retrieve quizzes with optional filtering
    - Submit quiz results: Students can submit their quiz answers and scores

Access Control:
    - Quiz creation: Restricted to teachers and administrative staff
    - Quiz viewing: Available to all authenticated users (teachers, staff, students)
    - Quiz submission: Restricted to students only (verified by roll_number attribute)
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.quiz import QuizInDB, QuizCreate, QuizResultCreate, QuizResultInDB
from app.crud import crud_quiz

router = APIRouter()

@router.post("/", response_model=QuizInDB)
def create_quiz(
    quiz_in: QuizCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff), # Admins/Teachers
) -> Any:
    """Create a new quiz.
    
    This endpoint allows teachers and administrative staff to create quizzes
    for their classes. The quiz creator's ID is automatically associated with
    the quiz as the teacher_id.
    
    Args:
        quiz_in: Quiz creation schema containing:
            - title: Quiz title/name
            - description: Optional quiz description
            - class_id: ID of the class this quiz belongs to
            - questions: List of quiz questions and answers
            - total_marks: Maximum score possible for the quiz
            - duration: Time limit in minutes (optional)
        db: Database session dependency injection
        current_user: Authenticated staff/teacher user (automatically verified)
    
    Authentication:
        Requires: Active staff or teacher account (JWT token)
        Role: Staff/Teacher (enforced by deps.get_current_active_staff)
    
    Returns:
        QuizInDB: Created quiz object including:
            - id: Unique quiz identifier
            - teacher_id: ID of the creating teacher
            - All fields from quiz_in
            - created_at: Timestamp of creation
    
    Raises:
        HTTPException:
            - 401: User not authenticated
            - 403: User is not staff/teacher
            - 422: Invalid input data (validation error)
    
    HTTP Status Codes:
        - 200: Quiz created successfully
        - 401: Unauthorized (not authenticated)
        - 403: Forbidden (not staff/teacher)
        - 422: Unprocessable Entity (validation failed)
    """
    return crud_quiz.create_quiz(db=db, quiz=quiz_in, teacher_id=str(current_user.id))

@router.get("/", response_model=List[QuizInDB])
def read_quizzes(
    db: Session = Depends(deps.get_db),
    class_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve a list of quizzes with optional filtering and pagination.
    
    This endpoint allows authenticated users (teachers, staff, and students)
    to retrieve quizzes. Results can be filtered by class and support pagination.
    
    Args:
        db: Database session dependency injection
        class_id: Optional filter to retrieve quizzes for a specific class.
            If None, returns quizzes from all classes (default: None)
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        current_user: Authenticated user (any active user type)
    
    Authentication:
        Requires: Active user account (JWT token)
        Role: Any authenticated user (student, teacher, or staff)
    
    Returns:
        List[QuizInDB]: List of quiz objects, each containing:
            - id: Unique quiz identifier
            - title: Quiz title
            - description: Quiz description
            - class_id: Associated class ID
            - teacher_id: Creator's user ID
            - questions: Quiz questions and answers
            - total_marks: Maximum possible score
            - duration: Time limit in minutes
            - created_at: Creation timestamp
    
    Raises:
        HTTPException:
            - 401: User not authenticated
            - 422: Invalid query parameters
    
    HTTP Status Codes:
        - 200: Quizzes retrieved successfully
        - 401: Unauthorized (not authenticated)
        - 422: Unprocessable Entity (invalid parameters)
    
    Example:
        GET /api/v1/quizzes?class_id=abc123&skip=0&limit=10
    """
    return crud_quiz.get_quizzes(db, class_id=class_id, skip=skip, limit=limit)

@router.post("/submit", response_model=QuizResultInDB)
def submit_quiz(
    result_in: QuizResultCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """Submit quiz results as a student.
    
    This endpoint allows students to submit their answers and scores for a quiz.
    Only users with student accounts (verified by roll_number attribute) can
    submit quiz results. The student's ID is automatically associated with
    the submission.
    
    Args:
        result_in: Quiz result submission schema containing:
            - quiz_id: ID of the quiz being submitted
            - answers: Student's answers to quiz questions
            - score: Points earned on the quiz
            - completed_at: Submission timestamp
        db: Database session dependency injection
        current_user: Authenticated user (must be a student)
    
    Authentication:
        Requires: Active student account (JWT token)
        Role: Student only (verified by presence of roll_number attribute)
    
    Returns:
        QuizResultInDB: Submitted quiz result object including:
            - id: Unique result identifier
            - quiz_id: Associated quiz ID
            - student_id: ID of the submitting student
            - answers: Submitted answers
            - score: Points earned
            - completed_at: Submission timestamp
            - created_at: Record creation timestamp
    
    Raises:
        HTTPException:
            - 400: User is not a student (missing roll_number attribute)
            - 401: User not authenticated
            - 404: Quiz with the specified quiz_id not found
            - 422: Invalid input data (validation error)
    
    HTTP Status Codes:
        - 200: Quiz result submitted successfully
        - 400: Bad Request (not a student account)
        - 401: Unauthorized (not authenticated)
        - 404: Not Found (quiz doesn't exist)
        - 422: Unprocessable Entity (validation failed)
    """
    # Verify that the current user is a student by checking for roll_number attribute
    # Students have a roll_number field, while teachers and staff do not
    if not hasattr(current_user, "roll_number"):
        raise HTTPException(status_code=400, detail="Only students can submit quiz results")
    
    # Submit the quiz result with the authenticated student's ID
    result = crud_quiz.submit_quiz_result(db, student_id=str(current_user.id), result_in=result_in)
    
    # Check if the quiz exists - crud function returns None if quiz not found
    if not result:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return result
