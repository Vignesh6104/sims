"""CRUD operations for student attendance tracking.

This module manages daily attendance records with UPSERT functionality
to prevent duplicate entries and provides class-level attendance reporting
with aggregated statistics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.attendance import Attendance
from app.models.student import Student
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate


def get_attendance(db: Session, attendance_id: str):
    """Retrieve a single attendance record by its unique identifier.
    
    Args:
        db: Database session for query execution.
        attendance_id: Unique identifier of the attendance record.
        
    Returns:
        Attendance object if found, None otherwise.
    """
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()


def get_attendance_by_student(db: Session, student_id: str, skip: int = 0, limit: int = 100):
    """Retrieve all attendance records for a specific student.
    
    Args:
        db: Database session for query execution.
        student_id: Unique identifier of the student.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Attendance objects for the specified student.
    """
    return db.query(Attendance).filter(Attendance.student_id == student_id).offset(skip).limit(limit).all()


def create_attendance(db: Session, attendance: AttendanceCreate):
    """Record attendance for a student with UPSERT logic.
    
    Includes an UPSERT mechanism: if a record already exists for the given 
    student and date, it updates the status and remarks instead of creating 
    a duplicate. This ensures data integrity for daily attendance logs.
    
    Args:
        db: Database session for query execution.
        attendance: AttendanceCreate schema with attendance details.
        
    Returns:
        Created or updated Attendance object.
        
    Note:
        UPSERT logic: Checks for existing student_id + date combination.
        If found, updates status and remarks; otherwise creates new record.
        This prevents duplicate attendance entries for the same day.
    """
    # Check if attendance already exists for this student on this date
    existing = db.query(Attendance).filter(
        Attendance.student_id == attendance.student_id,
        Attendance.date == attendance.date
    ).first()
    
    if existing:
        # Update existing record instead of creating duplicate
        existing.status = attendance.status
        existing.remarks = attendance.remarks
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new record if none exists
    db_attendance = Attendance(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


def update_attendance(db: Session, db_attendance: Attendance, attendance_update: AttendanceUpdate):
    """Update an existing attendance record.
    
    Supports partial updates for corrections or late entries.
    
    Args:
        db: Database session for query execution.
        db_attendance: Existing Attendance object to update.
        attendance_update: AttendanceUpdate schema with fields to update.
        
    Returns:
        Updated Attendance object.
    """
    update_data = attendance_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_attendance, key, value)
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


def get_attendance_report(db: Session, class_id: str):
    """Generate a comprehensive attendance report for a class.
    
    Uses SQL aggregation to calculate attendance statistics per student,
    including present, absent, and late counts with total days tracked.
    
    Args:
        db: Database session for query execution.
        class_id: Unique identifier of the class.
        
    Returns:
        List of dictionaries containing per-student statistics:
            - student_id: Student's unique identifier
            - student_name: Student's full name
            - roll_number: Student's roll number
            - present: Count of present days
            - absent: Count of absent days
            - late: Count of late arrivals
            - total_days: Total days of recorded attendance
            
    Note:
        Complex aggregation query with GROUP BY on student_id and status.
        Efficiently processes data at database level rather than in Python.
    """
    # Step 1: Get all students in the class
    students = db.query(Student).filter(Student.class_id == class_id).all()
    student_ids = [s.id for s in students]
    
    if not student_ids:
        return []

    # Step 2: Get aggregated attendance stats using SQL GROUP BY
    # Groups by student_id and status, counts occurrences
    stats = db.query(
        Attendance.student_id,
        Attendance.status,
        func.count(Attendance.id).label('count')
    ).filter(Attendance.student_id.in_(student_ids)).group_by(Attendance.student_id, Attendance.status).all()
    
    # Step 3: Process aggregated results into structured format
    report_data = {
        s.id: {
            'student_id': s.id,
            'student_name': s.full_name,
            'roll_number': s.roll_number,
            'present': 0, 
            'absent': 0, 
            'late': 0, 
            'total_days': 0
        } 
        for s in students
    }
    
    # Populate counts based on status
    for student_id, status, count in stats:
        if student_id in report_data:
            if status == 'present':
                report_data[student_id]['present'] = count
            elif status == 'absent':
                report_data[student_id]['absent'] = count
            elif status == 'late':
                report_data[student_id]['late'] = count
            
            report_data[student_id]['total_days'] += count

    return list(report_data.values())