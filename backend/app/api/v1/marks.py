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
    Download PDF Report Card
    """
    student = crud_student.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get marks
    marks = crud_marks.get_marks_by_student(db, student_id=student_id, skip=0, limit=1000)
    
    # Filter by exam if needed
    if exam_id:
        marks = [m for m in marks if m.exam_id == exam_id]

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
    Get aggregated marks report for a class.
    """
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
    Retrieve marks for a batch of students for a specific exam and subject.
    """
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
    Retrieve marks for a student.
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
    Add a mark/score.
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
    Update a mark.
    """
    mark = crud_marks.get_mark(db, mark_id=mark_id)
    if not mark:
        raise HTTPException(status_code=404, detail="Mark not found")
    return crud_marks.update_mark(db, db_mark=mark, mark_update=mark_in)