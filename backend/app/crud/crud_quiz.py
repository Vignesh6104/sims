"""CRUD operations for quiz management and automated grading.

This module handles quiz creation with JSON-based question storage,
quiz result submission, and automatic scoring based on correct answers.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.quiz import Quiz, QuizResult
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizResultCreate


def get_quiz(db: Session, quiz_id: str):
    """Retrieve a single quiz by its unique identifier.
    
    Args:
        db: Database session for query execution.
        quiz_id: Unique identifier of the quiz.
        
    Returns:
        Quiz object if found, None otherwise.
    """
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


def get_quizzes(db: Session, class_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    """Retrieve quizzes with optional class filtering.
    
    Args:
        db: Database session for query execution.
        class_id: Optional class ID to filter quizzes (default: None for all).
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Quiz objects, optionally filtered by class.
    """
    query = db.query(Quiz)
    if class_id:
        query = query.filter(Quiz.class_id == class_id)
    return query.offset(skip).limit(limit).all()


def create_quiz(db: Session, quiz: QuizCreate, teacher_id: str):
    """Create a new quiz with questions stored as JSON.
    
    Converts question schemas to JSON-serializable format for storage.
    
    Args:
        db: Database session for query execution.
        quiz: QuizCreate schema with quiz details and questions.
        teacher_id: Unique identifier of the teacher creating the quiz.
        
    Returns:
        Newly created Quiz object with generated ID.
        
    Note:
        Questions are stored as JSONB in the database for flexible querying.
        Each question includes: text, options, correct_answer, and points.
    """
    # Convert QuestionSchema list to JSON-serializable list of dicts
    questions_list = [q.dict() for q in quiz.questions_data]
    
    db_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        class_id=str(quiz.class_id),
        subject_id=str(quiz.subject_id),
        teacher_id=teacher_id,
        questions_data=questions_list,  # Stored as JSONB
        time_limit_minutes=quiz.time_limit_minutes,
        is_published=quiz.is_published
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def submit_quiz_result(db: Session, student_id: str, result_in: QuizResultCreate):
    """Submit and automatically grade a quiz attempt.
    
    Retrieves quiz questions, compares student answers with correct answers,
    calculates score based on question points, and stores the result.
    
    Args:
        db: Database session for query execution.
        student_id: Unique identifier of the student taking the quiz.
        result_in: QuizResultCreate schema with quiz_id and student answers.
        
    Returns:
        Newly created QuizResult object with calculated score, or None if quiz not found.
        
    Note:
        Automatic grading logic:
        - Iterates through questions from stored JSONB data
        - Compares student answer with correct_answer for each question
        - Accumulates points for correct answers
        - Handles variable point values per question
    """
    # Fetch the quiz to access questions and correct answers
    quiz = db.query(Quiz).filter(Quiz.id == str(result_in.quiz_id)).first()
    if not quiz:
        return None
    
    questions = quiz.questions_data
    score = 0
    total_points = 0
    
    # Automatic grading: compare answers with correct answers
    for i, q in enumerate(questions):
        points = q.get('points', 1.0)  # Default to 1 point if not specified
        total_points += points
        # Award points if answer matches correct answer
        if i < len(result_in.answers) and result_in.answers[i] == q['correct_answer']:
            score += points
            
    db_result = QuizResult(
        quiz_id=str(result_in.quiz_id),
        student_id=student_id,
        score=score,
        total_points=total_points,
        answers=result_in.answers  # Store student's answers for review
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result
