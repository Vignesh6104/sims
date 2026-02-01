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
    Get aggregated attendance report for a class.
    """
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
    Retrieve attendance records.
    """
    if student_id:
        attendance = crud_attendance.get_attendance_by_student(db, student_id=student_id, skip=skip, limit=limit)
    else:
        attendance = []
    return attendance

@router.post("/", response_model=Attendance)
def create_attendance(
    *,
    db: Session = Depends(deps.get_db),
    attendance_in: AttendanceCreate,
    current_user: Any = Depends(deps.get_current_active_staff), # Teachers/Admins
) -> Any:
    """
    Create new attendance record.
    """
    return crud_attendance.create_attendance(db, attendance=attendance_in)
