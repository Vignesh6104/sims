from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.attendance import Attendance
from app.models.student import Student
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate

def get_attendance(db: Session, attendance_id: str):
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()

def get_attendance_by_student(db: Session, student_id: str, skip: int = 0, limit: int = 100):
    return db.query(Attendance).filter(Attendance.student_id == student_id).offset(skip).limit(limit).all()

def create_attendance(db: Session, attendance: AttendanceCreate):
    db_attendance = Attendance(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def update_attendance(db: Session, db_attendance: Attendance, attendance_update: AttendanceUpdate):
    update_data = attendance_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_attendance, key, value)
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def get_attendance_report(db: Session, class_id: str):
    # 1. Get all students in the class
    students = db.query(Student).filter(Student.class_id == class_id).all()
    student_ids = [s.id for s in students]
    
    if not student_ids:
        return []

    # 2. Get aggregated stats per student
    stats = db.query(
        Attendance.student_id,
        Attendance.status,
        func.count(Attendance.id).label('count')
    ).filter(Attendance.student_id.in_(student_ids)).group_by(Attendance.student_id, Attendance.status).all()
    
    # 3. Process into a structured format
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