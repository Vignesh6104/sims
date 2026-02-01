from sqlalchemy.orm import Session
from app.models.marks import Mark
from app.models.student import Student
from app.models.exam import Exam
from app.schemas.marks import MarkCreate, MarkUpdate

def get_mark(db: Session, mark_id: str):
    return db.query(Mark).filter(Mark.id == mark_id).first()

def get_marks_by_student(db: Session, student_id: str, skip: int = 0, limit: int = 100):
    return db.query(Mark).filter(Mark.student_id == student_id).offset(skip).limit(limit).all()

def get_marks_by_filters(db: Session, student_ids: list[str], exam_id: str, subject: str):
    return db.query(Mark).filter(
        Mark.student_id.in_(student_ids),
        Mark.exam_id == exam_id,
        Mark.subject == subject
    ).all()

def create_mark(db: Session, mark: MarkCreate):
    db_mark = Mark(**mark.model_dump())
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    return db_mark

def update_mark(db: Session, db_mark: Mark, mark_update: MarkUpdate):
    update_data = mark_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mark, key, value)
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    return db_mark

def get_marks_report(db: Session, class_id: str):
    # Join Mark -> Student -> Exam
    results = db.query(Mark, Student, Exam).join(Student, Mark.student_id == Student.id).join(Exam, Mark.exam_id == Exam.id).filter(Student.class_id == class_id).all()
    
    report = []
    for mark, student, exam in results:
        report.append({
            "student_name": student.full_name,
            "roll_number": student.roll_number,
            "exam_name": exam.name,
            "date": exam.date,
            "subject": mark.subject,
            "score": mark.score,
            "max_score": mark.max_score,
            "percentage": round((mark.score / mark.max_score) * 100, 2) if mark.max_score > 0 else 0
        })
    return report