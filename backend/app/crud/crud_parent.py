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
    """
    Create a new parent account with hashed password.
    """
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

def update_parent(db: Session, db_parent: Parent, parent_update: ParentUpdate):
    """
    Update parent profile. Automatically hashes password if provided.
    """
    update_data = parent_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        db_parent.hashed_password = hashed_password
        
    for key, value in update_data.items():
        setattr(db_parent, key, value)
    db.add(db_parent)
    db.commit()
    db.refresh(db_parent)
    return db_parent
