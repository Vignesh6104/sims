from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.core.security import get_password_hash

def get_teacher(db: Session, teacher_id: str):
    return db.query(Teacher).filter(Teacher.id == teacher_id).first()

def get_teacher_by_email(db: Session, email: str):
    return db.query(Teacher).filter(Teacher.email == email).first()

def get_teachers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Teacher).offset(skip).limit(limit).all()

def create_teacher(db: Session, teacher: TeacherCreate):
    hashed_password = get_password_hash(teacher.password)
    db_teacher = Teacher(
        email=teacher.email,
        hashed_password=hashed_password,
        full_name=teacher.full_name,
        qualification=teacher.qualification,
        subject_specialization=teacher.subject_specialization,
        is_active=teacher.is_active
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def update_teacher(db: Session, db_teacher: Teacher, teacher_update: TeacherUpdate):
    update_data = teacher_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        db_teacher.hashed_password = hashed_password

    for key, value in update_data.items():
        setattr(db_teacher, key, value)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def delete_teacher(db: Session, teacher_id: str):
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if db_teacher:
        db.delete(db_teacher)
        db.commit()
    return db_teacher
