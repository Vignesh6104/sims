from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate

def get_subject(db: Session, subject_id: str):
    return db.query(Subject).filter(Subject.id == subject_id).first()

def get_subject_by_name(db: Session, name: str):
    return db.query(Subject).filter(Subject.name == name).first()

def get_subjects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Subject).offset(skip).limit(limit).all()

def create_subject(db: Session, subject: SubjectCreate):
    db_subject = Subject(name=subject.name, code=subject.code)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def update_subject(db: Session, db_subject: Subject, subject_update: SubjectUpdate):
    update_data = subject_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_subject, key, value)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def delete_subject(db: Session, subject_id: str):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if db_subject:
        db.delete(db_subject)
        db.commit()
    return db_subject
