from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io
from app.api import deps
from app.crud import crud_student
from app.schemas.student import Student, StudentCreate, StudentUpdate

router = APIRouter()

@router.post("/upload", response_model=dict)
def upload_students(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Bulk create students via CSV upload.
    CSV headers should be: email, password, full_name, roll_number, date_of_birth, address, class_id
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = file.file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(content))
    
    success_count = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=1):
        try:
            # Check for existing email
            if crud_student.get_student_by_email(db, email=row['email']):
                errors.append(f"Row {row_num}: Email {row['email']} already exists.")
                continue

            student_in = StudentCreate(
                email=row['email'],
                password=row['password'],
                full_name=row.get('full_name'),
                roll_number=row.get('roll_number'),
                date_of_birth=row.get('date_of_birth') if row.get('date_of_birth') else None,
                address=row.get('address'),
                class_id=row.get('class_id') if row.get('class_id') else None,
                is_active=True
            )
            crud_student.create_student(db, student=student_in)
            success_count += 1
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    return {
        "message": f"Processed {success_count} students successfully.",
        "success_count": success_count,
        "errors": errors
    }

@router.get("/", response_model=List[Student])
def read_students(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[str] = Query(None, description="Filter by Class ID"),
    current_user: Any = Depends(deps.get_current_active_staff), # Teachers/Admins
) -> Any:
    """
    Retrieve students. Optionally filter by class_id.
    """
    if class_id:
        return crud_student.get_students_by_class(db, class_id=class_id, skip=skip, limit=limit)
    return crud_student.get_students(db, skip=skip, limit=limit)

@router.post("/", response_model=Student)
def create_student(
    *,
    db: Session = Depends(deps.get_db),
    student_in: StudentCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin can manually create/force-add
) -> Any:
    """
    Create new student profile (Admin only).
    """
    student = crud_student.get_student_by_email(db, email=student_in.email)
    if student:
        raise HTTPException(status_code=400, detail="Student already exists")
    return crud_student.create_student(db, student=student_in)

@router.get("/{student_id}", response_model=Student)
def read_student(
    student_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get student by ID.
    """
    student = crud_student.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=Student)
def update_student(
    *,
    db: Session = Depends(deps.get_db),
    student_id: str,
    student_in: StudentUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Update student.
    """
    student = crud_student.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student = crud_student.update_student(db, db_student=student, student_update=student_in)
    return student

@router.delete("/{student_id}", response_model=Student)
def delete_student(
    *,
    db: Session = Depends(deps.get_db),
    student_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Delete student.
    """
    student = crud_student.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud_student.delete_student(db, student_id=student_id)