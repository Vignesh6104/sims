from sqlalchemy.orm import Session
from app.models.parent import Parent
from app.schemas.parent import ParentCreate, ParentUpdate
from app.core.security import get_password_hash

def get_parent(db: Session, parent_id: str):
    return db.query(Parent).filter(Parent.id == parent_id).first()

def get_parent_by_email(db: Session, email: str):
    return db.query(Parent).filter(Parent.email == email).first()

def get_parents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Parent).offset(skip).limit(limit).all()

def create_parent(db: Session, parent: ParentCreate):
    hashed_password = get_password_hash(parent.password)
    db_parent = Parent(
        email=parent.email,
        hashed_password=hashed_password,
        full_name=parent.full_name,
        phone_number=parent.phone_number,
        is_active=parent.is_active
    )
    db.add(db_parent)
    db.commit()
    db.refresh(db_parent)
    return db_parent

# Update parent logic is standard, skipping for brevity unless needed
