"""Dashboard API endpoints for aggregated statistics and metrics.

This module provides dashboard functionality for different user roles in the School
Information Management System (SIMS). It implements role-based access control and
optimized data aggregation to deliver fast, comprehensive statistics.

Purpose:
    - Provide aggregated data views for Admin, Teacher, and Student dashboards
    - Calculate performance metrics including attendance rates and exam averages
    - Generate chart-ready data for visualization components
    - Track recent activities and system trends

Features:
    - Admin Dashboard: System-wide statistics with monthly attendance trends
    - Teacher Dashboard: Class-specific stats with student performance tracking
    - Student Dashboard: Individual performance metrics with alerts
    
Access Control:
    - Admin stats: Requires active user authentication (any role)
    - Teacher stats: Requires staff/teacher authentication
    - Student stats: Requires active user authentication (student)
    
Performance Optimizations:
    - Bulk database queries to prevent N+1 query problems
    - Aggregation functions (COUNT, AVG, SUM) at database level
    - Selective column fetching for large datasets
    - Single-pass attendance and marks calculations
    - Conditional query execution based on data availability
    
Dependencies:
    - FastAPI for routing and dependency injection
    - SQLAlchemy for ORM and database aggregations
    - Authentication middleware for access control
"""
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
    
    This endpoint provides a comprehensive overview of the entire school system,
    including entity counts, monthly attendance trends, and recent activities.
    Designed for administrative users to monitor system health and growth.
    
    Parameters:
        db (Session): SQLAlchemy database session injected via dependency
        current_user (Any): Authenticated and active user from JWT token
        
    Authentication:
        Requires: Valid JWT token with active user status
        Role: Any authenticated user (typically admin)
        
    Returns:
        Dict[str, Any]: Dashboard statistics containing:
            - total_students (int): Total count of students in the system
            - total_teachers (int): Total count of teachers in the system
            - total_attendance_records (int): Total attendance entries recorded
            - total_classes (int): Total number of classrooms
            - chart_data (List[Dict]): Monthly attendance trends for current year
                Each entry: {"name": str, "students": int, "attendance": int}
            - recent_activities (List[Dict]): Recent system activities (max 5)
                Each entry: {"id": int, "text": str, "time": str, "type": str}
                
    HTTP Status Codes:
        200 OK: Statistics retrieved successfully
        401 Unauthorized: Missing or invalid authentication token
        403 Forbidden: User account is not active
        500 Internal Server Error: Database or server error
        
    Performance Notes:
        - Uses COUNT aggregations for efficiency
        - Separate queries are optimal for independent counts
        - Chart data limited to current year only
        - Recent activities capped at 5 entries total
    """
    # Database aggregation: Use scalar COUNT queries for efficient entity counting
    # Separate queries are faster than joins when counting independent tables
    total_students = db.query(func.count(Student.id)).scalar() or 0
    total_teachers = db.query(func.count(Teacher.id)).scalar() or 0
    total_attendance_records = db.query(func.count(Attendance.id)).scalar() or 0
    total_classes = db.query(func.count(ClassRoom.id)).scalar() or 0
    
    current_year = datetime.now().year
    
    # Database aggregation: Monthly attendance grouped by month for chart generation
    # Performance optimization: Filter by year BEFORE grouping to reduce dataset size
    attendance_data = db.query(
        extract('month', Attendance.date).label('month'),
        func.count(Attendance.id).label('count')
    ).filter(extract('year', Attendance.date) == current_year).group_by('month').all()
    
    # Create lookup map for O(1) access to monthly counts
    attendance_map = {int(month): count for month, count in attendance_data}
    
    # Chart data generation: Build 12-month trend data for visualization
    # Format: [{name: "Jan", students: total, attendance: count}, ...]
    chart_data = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for i, month_name in enumerate(months):
        month_num = i + 1
        chart_data.append({
            "name": month_name,
            "students": total_students,  # Total students for comparison
            "attendance": attendance_map.get(month_num, 0)  # Actual attendance count or 0
        })

    recent_activities = []
    # Performance optimization: Conditional queries - only execute if data exists
    # Selective column fetching: Only retrieve id, full_name, created_at (not entire row)
    if total_students > 0:
        new_students = db.query(Student.id, Student.full_name, Student.created_at).order_by(desc(Student.created_at)).limit(3).all()
        for s in new_students:
            recent_activities.append({
                "id": s.id,
                "text": f"New student joined: {s.full_name}",
                "time": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "Unknown", 
                "type": "student"
            })
    
    # Fetch recent teachers separately to maintain separate limits (3 students, 2 teachers)
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
    
    This endpoint provides teachers with comprehensive insights into their assigned
    classes, including today's attendance, marks entry progress, and individual
    student performance metrics. Optimized to handle large class sizes efficiently.
    
    Parameters:
        db (Session): SQLAlchemy database session injected via dependency
        current_user (Any): Authenticated staff/teacher user from JWT token
        
    Authentication:
        Requires: Valid JWT token with active staff status
        Role: Teacher or staff member only
        
    Returns:
        Dict[str, Any]: Teacher-specific dashboard data containing:
            - date (date): Current date for context
            - overview (Dict): Today's attendance summary
                - present (int): Students marked present or late today
                - absent (int): Students marked absent today
                - pending_marks (int): Classes with incomplete marks entry
            - classes (List[Dict]): Teacher's assigned classes
                Each: {"id": int, "name": str}
            - marks_status (List[Dict]): Marks entry progress per class
                Each: {"exam_name": str, "class_name": str, "status": str, "progress": str}
            - students (List[Dict]): All students with performance data
                Each: {"id", "roll_number", "full_name", "class_name", 
                       "attendance_pct": float, "avg_marks": float}
            - recent_activity (List[Dict]): Recent teacher activities
                Each: {"title": str, "desc": str, "time": str}
                
    HTTP Status Codes:
        200 OK: Statistics retrieved successfully
        401 Unauthorized: Missing or invalid authentication token
        403 Forbidden: User is not staff/teacher or account inactive
        500 Internal Server Error: Database or server error
        
    Performance Optimizations:
        - Bulk queries replace N+1 patterns for student details
        - Class-level aggregation for marks entry status
        - Single-pass attendance and marks calculations
        - Grouped database queries for student counts and marks
    """
    teacher_id = current_user.id
    # Fetch all classes assigned to this teacher
    classes = db.query(ClassRoom).filter(ClassRoom.teacher_id == teacher_id).all()
    class_ids = [c.id for c in classes]
    
    # Bulk fetch: Get all students across teacher's classes at once (prevents N+1)
    students = db.query(Student).filter(Student.class_id.in_(class_ids)).all()
    student_ids = [s.id for s in students]
    
    today = datetime.now().date()
    present_today = 0
    absent_today = 0
    
    # Database aggregation: Group attendance by status for today
    # Performance: Single query replaces per-student lookups
    if student_ids:
        attendance_today = db.query(
            Attendance.status, 
            func.count(Attendance.id)
        ).filter(
            Attendance.student_id.in_(student_ids), 
            Attendance.date == today
        ).group_by(Attendance.status).all()
        
        # Attendance status matching: Handle both Enum objects and string values
        # Robust handling ensures compatibility with different database configurations
        for status, count in attendance_today:
            # Extract value from Enum or use string directly
            status_val = status.value if hasattr(status, 'value') else str(status)
            if status_val in ['present', 'late']:
                present_today += count
            elif status_val == 'absent':
                absent_today += count

    

    # Get the most recent exam for marks entry tracking
    latest_exam = db.query(Exam).order_by(Exam.date.desc()).first()
    marks_status = []
    pending_count = 0

    # Performance optimization: Bulk aggregation for marks entry status
    # Avoids N+1 query pattern (one query per class) by using grouped queries
    if latest_exam and class_ids:
        # Database aggregation: Count students per class in a single grouped query
        class_student_counts = db.query(
            Student.class_id,
            func.count(Student.id).label('count')
        ).filter(Student.class_id.in_(class_ids)).group_by(Student.class_id).all()
        class_student_map = {c.class_id: c.count for c in class_student_counts}

        # Database aggregation: Count marks entered per class for latest exam
        # Join ensures we only count marks that belong to students in teacher's classes
        marks_entered_counts = db.query(
            Student.class_id,
            func.count(Mark.id).label('count')
        ).join(Mark, Mark.student_id == Student.id).filter(
            Student.class_id.in_(class_ids),
            Mark.exam_id == latest_exam.id
        ).group_by(Student.class_id).all()
        marks_entered_map = {m.class_id: m.count for m in marks_entered_counts}

        # Role-based stat calculation: Determine completion status per class
        for cls in classes:
            cls_student_count = class_student_map.get(cls.id, 0)
            marks_entered = marks_entered_map.get(cls.id, 0)
            
            # Status logic: Completed if all students have marks entered
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
    # Performance optimization: Prevent N+1 queries for student statistics
    # CRITICAL: Instead of querying per student, fetch all stats in two bulk queries
    if student_ids:
        # Database aggregation: Bulk fetch attendance stats for all students
        # Uses CASE for conditional counting (present + late = attended)
        attendance_stats = db.query(
            Attendance.student_id,
            func.count(Attendance.id).label('total'),
            func.count(case((Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]), 1))).label('present')
        ).filter(Attendance.student_id.in_(student_ids)).group_by(Attendance.student_id).all()
        
        # Create lookup map for O(1) access: {student_id: (total, present)}
        att_map = {stat.student_id: (stat.total, stat.present) for stat in attendance_stats}

        # Database aggregation: Bulk fetch average marks for all students in one query
        mark_stats = db.query(
            Mark.student_id,
            func.avg(Mark.score).label('avg')
        ).filter(Mark.student_id.in_(student_ids)).group_by(Mark.student_id).all()
        
        # Create lookup map for O(1) access: {student_id: avg_score}
        mark_map = {stat.student_id: stat.avg for stat in mark_stats}

        # Single-pass calculation: Combine fetched data with student records
        for s in students:
            total_att, present_att = att_map.get(s.id, (0, 0))
            # Calculate attendance percentage, handle division by zero
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
    Retrieve personalized statistics for Student Dashboard.
    
    This endpoint provides individual students with their academic performance
    metrics including attendance percentage, exam averages, class information,
    and personalized alerts based on their performance thresholds.
    
    Parameters:
        db (Session): SQLAlchemy database session injected via dependency
        current_user (Any): Authenticated student user from JWT token
        
    Authentication:
        Requires: Valid JWT token with active user status
        Role: Student (authenticated user accessing their own data)
        
    Returns:
        Dict[str, Any]: Student-specific dashboard data containing:
            - attendance (Dict): Attendance statistics
                - percentage (float): Overall attendance percentage
                - status (str): "Good" (>=75%), "Warning" (<75%), or "Shortage" (<60%)
                - last_marked (date): Date of last attendance record
            - marks (Dict): Academic performance metrics
                - total_exams (int): Number of exams taken
                - average (float): Average score across all exams
                - latest_result (str): "score/max_score in subject" or None
            - classroom (Dict): Class assignment info
                - name (str): Classroom name or "Not Assigned"
                - section (str): Section identifier (currently placeholder)
            - alerts (List[Dict]): Performance warnings and notifications
                Each: {"type": str, "msg": str}
                
    HTTP Status Codes:
        200 OK: Statistics retrieved successfully
        401 Unauthorized: Missing or invalid authentication token
        403 Forbidden: User account is not active
        500 Internal Server Error: Database or server error
        
    Performance Notes:
        - Direct queries filtered by student_id (indexed)
        - Minimal joins for fast response
        - Alert generation based on thresholds (75% and 60% attendance)
    """
    student_id = current_user.id
    
    # Database aggregation: Calculate total and present attendance counts
    # Attendance status matching: Consider both PRESENT and LATE as attended
    total_att = db.query(func.count(Attendance.id)).filter(Attendance.student_id == student_id).scalar() or 0
    present_att = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id, 
        Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
    ).scalar() or 0
    # Calculate percentage with proper division-by-zero handling
    att_pct = round((present_att / total_att * 100), 1) if total_att and total_att > 0 else 0.0
    
    # Get most recent attendance record for "last marked" display
    last_attendance = db.query(Attendance).filter(Attendance.student_id == student_id).order_by(Attendance.date.desc()).first()
    
    # Database aggregation: Calculate exam count and average marks
    total_exams = db.query(func.count(Mark.id)).filter(Mark.student_id == student_id).scalar() or 0
    avg_marks = db.query(func.avg(Mark.score)).filter(Mark.student_id == student_id).scalar() or 0.0
    
    # Get latest exam result by joining with Exam table and ordering by exam date
    latest_mark = db.query(Mark).filter(Mark.student_id == student_id).join(Exam).order_by(Exam.date.desc()).first()
    
    # Fetch classroom information if student is assigned to a class
    student_class = None
    if current_user.class_id:
        student_class = db.query(ClassRoom).filter(ClassRoom.id == current_user.class_id).first()
    
    # Role-based stat calculation: Determine attendance status based on thresholds
    # Good: >= 75%, Warning: 60-75%, Shortage: < 60%
    att_status = "Good"
    if att_pct < 75: att_status = "Warning"
    if att_pct < 60: att_status = "Shortage"
    
    # Generate personalized alerts based on performance metrics
    alerts_list = []
    # Attendance warning if below 75% (but above 0 to avoid false alerts)
    if att_pct < 75 and att_pct > 0:
        alerts_list.append({"type": "warning", "msg": "Attendance below 75%!"})
    # Info alert for new exam results
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