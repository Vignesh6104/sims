from sqlalchemy.orm import Session
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.core.security import get_password_hash

def get_student(db: Session, student_id: str):
    return db.query(Student).filter(Student.id == student_id).first()

def get_student_by_email(db: Session, email: str):
    return db.query(Student).filter(Student.email == email).first()

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Student).offset(skip).limit(limit).all()

def get_students_by_class(db: Session, class_id: str, skip: int = 0, limit: int = 100):
    return db.query(Student).filter(Student.class_id == class_id).offset(skip).limit(limit).all()

def create_student(db: Session, student: StudentCreate):
    hashed_password = get_password_hash(student.password)
    db_student = Student(
        email=student.email,
        hashed_password=hashed_password,
        full_name=student.full_name,
        roll_number=student.roll_number,
        date_of_birth=student.date_of_birth,
        address=student.address,
        class_id=student.class_id,
        is_active=student.is_active
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, db_student: Student, student_update: StudentUpdate):
    update_data = student_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        db_student.hashed_password = hashed_password
        
    for key, value in update_data.items():
        setattr(db_student, key, value)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: str):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
    return db_student