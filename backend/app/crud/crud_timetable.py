from sqlalchemy.orm import Session
from app.models.timetable import Timetable
from app.schemas.timetable import TimetableCreate, TimetableUpdate

def get_timetable_by_class(db: Session, class_id: str):
    return db.query(Timetable).filter(Timetable.class_id == class_id).all()

def get_timetable_by_teacher(db: Session, teacher_id: str):
    return db.query(Timetable).filter(Timetable.teacher_id == teacher_id).all()

def create_timetable_entry(db: Session, timetable_in: TimetableCreate):
    # Optional: Check for conflicts (same teacher/class at same time)
    # For MVP, just create
    db_entry = Timetable(**timetable_in.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def delete_timetable_entry(db: Session, entry_id: str):
    entry = db.query(Timetable).filter(Timetable.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
    return entry
