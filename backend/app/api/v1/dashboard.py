from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, case
from app.api import deps
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.attendance import Attendance, AttendanceStatus
from app.models.class_room import ClassRoom
from app.models.marks import Mark
from app.models.exam import Exam
from datetime import datetime

router = APIRouter()

@router.get("/stats", response_model=Dict[str, Any])
def read_stats(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve high-level system statistics for the Admin Dashboard.
    
    This endpoint uses optimized aggregated queries to fetch total counts for students, 
    teachers, classes, and attendance records. It also calculates monthly attendance 
    trends for the current year.
    
    Args:
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        A dictionary containing counts, chart data for trends, and a list of recent activities.
    """
    # Use a single query to get all counts if possible, or keep separate but ensure they are efficient
    total_students = db.query(func.count(Student.id)).scalar() or 0
    total_teachers = db.query(func.count(Teacher.id)).scalar() or 0
    total_attendance_records = db.query(func.count(Attendance.id)).scalar() or 0
    total_classes = db.query(func.count(ClassRoom.id)).scalar() or 0
    
    current_year = datetime.now().year
    
    # Get monthly attendance counts - Optimized with filter before group_by
    attendance_data = db.query(
        extract('month', Attendance.date).label('month'),
        func.count(Attendance.id).label('count')
    ).filter(extract('year', Attendance.date) == current_year).group_by('month').all()
    
    attendance_map = {int(month): count for month, count in attendance_data}
    
    chart_data = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for i, month_name in enumerate(months):
        month_num = i + 1
        chart_data.append({
            "name": month_name,
            "students": total_students,
            "attendance": attendance_map.get(month_num, 0)
        })

    recent_activities = []
    # Only fetch if counts > 0, and ensure we only get necessary columns for speed
    if total_students > 0:
        new_students = db.query(Student.id, Student.full_name, Student.created_at).order_by(desc(Student.created_at)).limit(3).all()
        for s in new_students:
            recent_activities.append({
                "id": s.id,
                "text": f"New student joined: {s.full_name}",
                "time": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "Unknown", 
                "type": "student"
            })
    
    if total_teachers > 0:
        new_teachers = db.query(Teacher.id, Teacher.full_name, Teacher.created_at).order_by(desc(Teacher.created_at)).limit(2).all()
        for t in new_teachers:
            recent_activities.append({
                "id": t.id,
                "text": f"New teacher hired: {t.full_name}",
                "time": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "Unknown",
                "type": "teacher"
            })
    
    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_attendance_records": total_attendance_records,
        "total_classes": total_classes,
        "chart_data": chart_data,
        "recent_activities": recent_activities
    }

@router.get("/teacher/stats", response_model=Dict[str, Any])
def read_teacher_stats(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Retrieve detailed classroom statistics for the Teacher Dashboard.
    
    Performance Optimizations:
    - Replaced N+1 student detail queries with bulk aggregation.
    - Optimized marks entry status with class-level grouped counts.
    - Robust attendance status matching (handles both Enums and raw strings).
    - Prevents timeouts on large student datasets.
    
    Args:
        db: Database session.
        current_user: Authenticated staff member (Teacher).
        
    Returns:
        Overview counts (present/absent), assigned classes, marks entry progress, 
        and student-specific performance metrics.
    """
    teacher_id = current_user.id
    classes = db.query(ClassRoom).filter(ClassRoom.teacher_id == teacher_id).all()
    class_ids = [c.id for c in classes]
    
    students = db.query(Student).filter(Student.class_id.in_(class_ids)).all()
    student_ids = [s.id for s in students]
    
    today = datetime.now().date()
    present_today = 0
    absent_today = 0
    
    if student_ids:
        attendance_today = db.query(
            Attendance.status, 
            func.count(Attendance.id)
        ).filter(
            Attendance.student_id.in_(student_ids), 
            Attendance.date == today
        ).group_by(Attendance.status).all()
        
        for status, count in attendance_today:
            # Handle both enum objects and raw strings
            status_val = status.value if hasattr(status, 'value') else str(status)
            if status_val in ['present', 'late']:
                present_today += count
            elif status_val == 'absent':
                absent_today += count

    

    latest_exam = db.query(Exam).order_by(Exam.date.desc()).first()
    marks_status = []
    pending_count = 0

    if latest_exam and class_ids:
        # Get student counts per class
        class_student_counts = db.query(
            Student.class_id,
            func.count(Student.id).label('count')
        ).filter(Student.class_id.in_(class_ids)).group_by(Student.class_id).all()
        class_student_map = {c.class_id: c.count for c in class_student_counts}

        # Get marks entered per class for the latest exam
        marks_entered_counts = db.query(
            Student.class_id,
            func.count(Mark.id).label('count')
        ).join(Mark, Mark.student_id == Student.id).filter(
            Student.class_id.in_(class_ids),
            Mark.exam_id == latest_exam.id
        ).group_by(Student.class_id).all()
        marks_entered_map = {m.class_id: m.count for m in marks_entered_counts}

        for cls in classes:
            cls_student_count = class_student_map.get(cls.id, 0)
            marks_entered = marks_entered_map.get(cls.id, 0)
            
            status = "Completed" if marks_entered >= cls_student_count and cls_student_count > 0 else "Pending"
            if status == "Pending" and cls_student_count > 0:
                pending_count += 1
                
            marks_status.append({
                "exam_name": latest_exam.name,
                "class_name": cls.name,
                "status": status,
                "progress": f"{marks_entered}/{cls_student_count}"
            })



    student_details = []
    if student_ids:
        # Optimized: Fetch all attendance stats in one query
        attendance_stats = db.query(
            Attendance.student_id,
            func.count(Attendance.id).label('total'),
            func.count(case((Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]), 1))).label('present')
        ).filter(Attendance.student_id.in_(student_ids)).group_by(Attendance.student_id).all()
        
        att_map = {stat.student_id: (stat.total, stat.present) for stat in attendance_stats}

        # Optimized: Fetch all average marks in one query
        mark_stats = db.query(
            Mark.student_id,
            func.avg(Mark.score).label('avg')
        ).filter(Mark.student_id.in_(student_ids)).group_by(Mark.student_id).all()
        
        mark_map = {stat.student_id: stat.avg for stat in mark_stats}

        for s in students:
            total_att, present_att = att_map.get(s.id, (0, 0))
            att_pct = round((present_att / total_att * 100), 1) if total_att > 0 else 0.0
            
            avg_mark = mark_map.get(s.id, 0.0)
            
            student_details.append({
                "id": s.id,
                "roll_number": s.roll_number,
                "full_name": s.full_name,
                "class_name": next((c.name for c in classes if c.id == s.class_id), "N/A"),
                "attendance_pct": att_pct,
                "avg_marks": round(float(avg_mark), 1) if avg_mark else 0.0
            })



    



    recent_activity = []

    if present_today > 0 or absent_today > 0:

        recent_activity.append({

            "title": "Attendance Marked",

            "desc": f"Marked for {today}",

            "time": "Today"

        })

    if pending_count > 0:

        recent_activity.append({

            "title": "Pending Marks",

            "desc": f"{pending_count} classes need marks entry",

            "time": "Action Required"

        })
    return {
        "date": today,
        "overview": {
            "present": present_today,
            "absent": absent_today,
            "pending_marks": pending_count
        },
        "classes": [{"id": c.id, "name": c.name} for c in classes],
        "marks_status": marks_status,
        "students": student_details,
        "recent_activity": recent_activity
    }

@router.get("/student/stats", response_model=Dict[str, Any])
def read_student_stats(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user), # Student
) -> Any:
    """
    Get detailed statistics for Student Dashboard.
    """
    student_id = current_user.id
    
    # 1. Attendance Stats
    total_att = db.query(func.count(Attendance.id)).filter(Attendance.student_id == student_id).scalar() or 0
    present_att = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id, 
        Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
    ).scalar() or 0
    att_pct = round((present_att / total_att * 100), 1) if total_att and total_att > 0 else 0.0
    
    last_attendance = db.query(Attendance).filter(Attendance.student_id == student_id).order_by(Attendance.date.desc()).first()
    
    # 2. Marks Stats
    total_exams = db.query(func.count(Mark.id)).filter(Mark.student_id == student_id).scalar() or 0
    avg_marks = db.query(func.avg(Mark.score)).filter(Mark.student_id == student_id).scalar() or 0.0
    
    latest_mark = db.query(Mark).filter(Mark.student_id == student_id).join(Exam).order_by(Exam.date.desc()).first()
    
    # 3. Class Info
    student_class = None
    if current_user.class_id:
        student_class = db.query(ClassRoom).filter(ClassRoom.id == current_user.class_id).first()
    
    # 4. Status Determination
    att_status = "Good"
    if att_pct < 75: att_status = "Warning"
    if att_pct < 60: att_status = "Shortage"
    
    alerts_list = []
    if att_pct < 75 and att_pct > 0:
        alerts_list.append({"type": "warning", "msg": "Attendance below 75%!"})
    if latest_mark: # Only add if there's a latest mark
        alerts_list.append({"type": "info", "msg": "New exam results published"})

    return {
        "attendance": {
            "percentage": att_pct,
            "status": att_status,
            "last_marked": last_attendance.date if last_attendance else None
        },
        "marks": {
            "total_exams": total_exams,
            "average": avg_marks,
            "latest_result": f"{latest_mark.score}/{latest_mark.max_score} in {latest_mark.subject}" if latest_mark else None
        },
        "classroom": {
            "name": student_class.name if student_class else "Not Assigned",
            "section": "A" # Placeholder
        },
        "alerts": alerts_list
    }