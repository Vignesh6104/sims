"""CRUD operations for assignment and submission management.

This module handles homework/assignment creation by teachers and submission
tracking by students. Includes JOIN operations for enriched data retrieval
and grading functionality.
"""

from sqlalchemy.orm import Session
from app.models.assignment import Assignment, Submission
from app.models.student import Student
from app.schemas.assignment import AssignmentCreate, SubmissionCreate, SubmissionUpdate


def get_assignments_by_class(db: Session, class_id: str):
    """Retrieve all assignments for a specific class.
    
    Args:
        db: Database session for query execution.
        class_id: Unique identifier of the class.
        
    Returns:
        List of Assignment objects for the specified class.
    """
    return db.query(Assignment).filter(Assignment.class_id == class_id).all()


def get_assignments_by_teacher(db: Session, teacher_id: str):
    """Retrieve all assignments created by a specific teacher.
    
    Args:
        db: Database session for query execution.
        teacher_id: Unique identifier of the teacher.
        
    Returns:
        List of Assignment objects created by the teacher.
    """
    return db.query(Assignment).filter(Assignment.teacher_id == teacher_id).all()


def create_assignment(db: Session, assignment: AssignmentCreate):
    """Create a new assignment.
    
    Args:
        db: Database session for query execution.
        assignment: AssignmentCreate schema with assignment details.
        
    Returns:
        Newly created Assignment object with generated ID.
    """
    db_assignment = Assignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def get_submissions_by_assignment(db: Session, assignment_id: str):
    """Fetch all submissions for a specific assignment with student names.
    
    Performs a JOIN with the Student table for efficient data retrieval,
    enriching submissions with student information.
    
    Args:
        db: Database session for query execution.
        assignment_id: Unique identifier of the assignment.
        
    Returns:
        List of Submission objects with added student_name attribute.
        
    Note:
        Uses JOIN for efficiency instead of N+1 queries.
        Dynamically adds student_name to submission objects.
    """
    # JOIN query to fetch submissions with student names in one query
    results = db.query(Submission, Student.full_name)\
        .join(Student, Submission.student_id == Student.id)\
        .filter(Submission.assignment_id == assignment_id)\
        .all()
    
    submissions = []
    for sub, name in results:
        # Enrich submission object with student name
        sub.student_name = name
        submissions.append(sub)
    
    return submissions


def get_submission_by_student(db: Session, assignment_id: str, student_id: str):
    """Retrieve a single submission for a specific student and assignment.
    
    Used to check if a student has already submitted an assignment.
    
    Args:
        db: Database session for query execution.
        assignment_id: Unique identifier of the assignment.
        student_id: Unique identifier of the student.
        
    Returns:
        Submission object if found, None otherwise.
    """
    return db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == student_id
    ).first()


def get_all_submissions_by_student(db: Session, student_id: str):
    """Retrieve all submissions made by a specific student with student name.
    
    Useful for the student's own assignment view and submission history.
    
    Args:
        db: Database session for query execution.
        student_id: Unique identifier of the student.
        
    Returns:
        List of Submission objects with added student_name attribute.
        
    Note:
        Includes JOIN with Student table for consistent data structure.
    """
    # JOIN query for submissions with student details
    results = db.query(Submission, Student.full_name)\
        .join(Student, Submission.student_id == Student.id)\
        .filter(Submission.student_id == student_id)\
        .all()
    
    submissions = []
    for sub, name in results:
        # Enrich submission object with student name
        sub.student_name = name
        submissions.append(sub)
    
    return submissions


def create_submission(db: Session, submission: SubmissionCreate):
    """Create a new assignment submission by a student.
    
    Args:
        db: Database session for query execution.
        submission: SubmissionCreate schema with submission details.
        
    Returns:
        Newly created Submission object with generated ID.
    """
    db_submission = Submission(**submission.model_dump())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission


def update_submission(db: Session, db_submission: Submission, submission_update: SubmissionUpdate):
    """Update an existing submission with grade and feedback.
    
    Used by teachers to grade submitted assignments.
    
    Args:
        db: Database session for query execution.
        db_submission: Existing Submission object to update.
        submission_update: SubmissionUpdate schema with grade and/or feedback.
        
    Returns:
        Updated Submission object.
        
    Note:
        Only updates fields if they are not None in the update schema.
    """
    # Update only if values are provided
    if submission_update.grade is not None:
        db_submission.grade = submission_update.grade
    if submission_update.feedback is not None:
        db_submission.feedback = submission_update.feedback
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission
