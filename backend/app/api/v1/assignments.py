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
    
    # Upload file to Cloudinary
    temp_file_path = None
    try:
        # Create a named temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name # Get the path of the temporary file
            
        upload_result = cloudinary.uploader.upload(
            temp_file_path, 
            folder="sims_assignments",
            resource_type="auto"
        )
        file_url = upload_result.get("secure_url") or upload_result.get("url")
        if not file_url:
            raise HTTPException(status_code=500, detail="Cloudinary upload failed: No URL returned")
        
        file_url = str(file_url) # Ensure it's a string
            
    except cloudinary.exceptions.Error as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload processing failed: {e}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path) # Clean up the temporary file

    if existing:
        # Update existing submission
        # Optionally, delete old file from Cloudinary here if needed, requires public_id
        
        existing.content = file_url
        existing.submission_date = date.today()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new submission record
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
