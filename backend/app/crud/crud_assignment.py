from sqlalchemy.orm import Session
from app.models.assignment import Assignment, Submission
from app.schemas.assignment import AssignmentCreate, SubmissionCreate, SubmissionUpdate

def get_assignments_by_class(db: Session, class_id: str):
    return db.query(Assignment).filter(Assignment.class_id == class_id).all()

def get_assignments_by_teacher(db: Session, teacher_id: str):
    return db.query(Assignment).filter(Assignment.teacher_id == teacher_id).all()

def create_assignment(db: Session, assignment: AssignmentCreate):
    db_assignment = Assignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_submissions_by_assignment(db: Session, assignment_id: str):
    return db.query(Submission).filter(Submission.assignment_id == assignment_id).all()

def get_submission_by_student(db: Session, assignment_id: str, student_id: str):
    return db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == student_id
    ).first()

def get_all_submissions_by_student(db: Session, student_id: str):
    return db.query(Submission).filter(Submission.student_id == student_id).all()

def create_submission(db: Session, submission: SubmissionCreate):
    db_submission = Submission(**submission.model_dump())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def update_submission(db: Session, db_submission: Submission, submission_update: SubmissionUpdate):
    if submission_update.grade is not None:
        db_submission.grade = submission_update.grade
    if submission_update.feedback is not None:
        db_submission.feedback = submission_update.feedback
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission
