from sqlalchemy.orm import Session

from app.crud import crud_admin
from app.schemas.admin import AdminCreate
from app.core.config import settings
from app.db import base  # noqa: F401

def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    
    admin = crud_admin.get_admin_by_email(db, email="admin@school.com")
    if not admin:
        admin_in = AdminCreate(
            email="admin@school.com",
            password="admin",
            full_name="Super Admin",
            department="IT",
            position="System Administrator"
        )
        crud_admin.create_admin(db, admin=admin_in)