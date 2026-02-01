from sqlalchemy.orm import Session
from app.models.exam import Exam
from app.schemas.exam import ExamCreate, ExamUpdate

def get_exam(db: Session, exam_id: str):
    return db.query(Exam).filter(Exam.id == exam_id).first()

def get_exams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Exam).offset(skip).limit(limit).all()

def create_exam(db: Session, exam: ExamCreate):
    db_exam = Exam(name=exam.name, date=exam.date)
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def update_exam(db: Session, db_exam: Exam, exam_update: ExamUpdate):
    update_data = exam_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exam, key, value)
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def delete_exam(db: Session, exam_id: str):
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if db_exam:
        db.delete(db_exam)
        db.commit()
    return db_exam
