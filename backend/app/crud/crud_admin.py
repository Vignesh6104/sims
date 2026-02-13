from sqlalchemy.orm import Session
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminUpdate
from app.core.security import get_password_hash

def get_admin(db: Session, admin_id: str):
    return db.query(Admin).filter(Admin.id == admin_id).first()

def get_admin_by_email(db: Session, email: str):
    return db.query(Admin).filter(Admin.email == email).first()

def get_admins(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Admin).offset(skip).limit(limit).all()

def create_admin(db: Session, admin: AdminCreate):
    hashed_password = get_password_hash(admin.password)
    db_admin = Admin(
        email=admin.email,
        hashed_password=hashed_password,
        full_name=admin.full_name,
        department=admin.department,
        position=admin.position,
        is_active=admin.is_active
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def update_admin(db: Session, db_admin: Admin, admin_update: AdminUpdate):
    update_data = admin_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        db_admin.hashed_password = hashed_password
    
    for key, value in update_data.items():
        setattr(db_admin, key, value)

    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def delete_admin(db: Session, admin_id: str):
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if db_admin:
        db.delete(db_admin)
        db.commit()
    return db_admin
