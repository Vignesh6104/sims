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

router = APIRouter()

UPLOAD_DIR = "uploads/assignments"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.get("/class/{class_id}", response_model=List[Assignment])
def read_class_assignments(
    class_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_assignment.get_assignments_by_class(db, class_id=class_id)

@router.get("/teacher", response_model=List[Assignment])
def read_teacher_assignments(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    # Assuming current_user is a Teacher
    return crud_assignment.get_assignments_by_teacher(db, teacher_id=current_user.id)

@router.post("/", response_model=Assignment)
def create_assignment(
    *,
    db: Session = Depends(deps.get_db),
    assignment_in: AssignmentCreate,
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    return crud_assignment.create_assignment(db, assignment=assignment_in)

@router.post("/submissions", response_model=Submission)
async def submit_assignment(
    *,
    db: Session = Depends(deps.get_db),
    assignment_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    # Check if already submitted
    existing = crud_assignment.get_submission_by_student(db, assignment_id=assignment_id, student_id=current_user.id)
    
    if existing and existing.grade is not None:
        raise HTTPException(status_code=400, detail="Assignment already graded and cannot be edited")
    
    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    content_path = f"/uploads/assignments/{file_name}"

    if existing:
        # Update existing submission
        # Delete old file if possible (optional but good practice)
        old_file_path = existing.content.lstrip('/')
        if os.path.exists(old_file_path):
            try: os.remove(old_file_path)
            except: pass
            
        existing.content = content_path
        existing.submission_date = date.today()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new submission record
    submission_in = SubmissionCreate(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=content_path,
        submission_date=date.today()
    )
    
    return crud_assignment.create_submission(db, submission=submission_in)

@router.get("/submissions/{assignment_id}", response_model=List[Submission])
def read_submissions(
    assignment_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    return crud_assignment.get_submissions_by_assignment(db, assignment_id=assignment_id)

@router.get("/my-submissions", response_model=List[Submission])
def read_my_submissions(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_assignment.get_all_submissions_by_student(db, student_id=current_user.id)

@router.put("/submissions/{submission_id}", response_model=Submission)
def grade_submission(
    submission_id: str,
    submission_in: SubmissionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    # Need to fetch the submission first... simplified:
    # We don't have get_submission_by_id in crud yet, adding direct query here for speed
    from app.models.assignment import Submission as SubmissionModel
    db_sub = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return crud_assignment.update_submission(db, db_submission=db_sub, submission_update=submission_in)
