"""CRUD operations for Admin user management.

This module provides Create, Read, Update, and Delete operations for
administrative users in the School Information Management System.
Handles user authentication, password hashing, and account management.
"""

from sqlalchemy.orm import Session
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminUpdate
from app.core.security import get_password_hash


def get_admin(db: Session, admin_id: str):
    """Retrieve a single admin by their unique identifier.
    
    Args:
        db: Database session for query execution.
        admin_id: Unique identifier of the admin.
        
    Returns:
        Admin object if found, None otherwise.
    """
    return db.query(Admin).filter(Admin.id == admin_id).first()


def get_admin_by_email(db: Session, email: str):
    """Retrieve an admin by their email address.
    
    Used primarily for authentication and duplicate email checking.
    
    Args:
        db: Database session for query execution.
        email: Email address to search for.
        
    Returns:
        Admin object if found, None otherwise.
    """
    return db.query(Admin).filter(Admin.email == email).first()


def get_admins(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a paginated list of all admins.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Admin objects.
    """
    return db.query(Admin).offset(skip).limit(limit).all()


def create_admin(db: Session, admin: AdminCreate):
    """Create a new admin account with hashed password.
    
    Args:
        db: Database session for query execution.
        admin: AdminCreate schema with admin details including password.
        
    Returns:
        Newly created Admin object with generated ID.
        
    Note:
        Password is automatically hashed using bcrypt before storage.
    """
    # Hash the password before storing
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
    """Update existing admin information.
    
    Supports partial updates using Pydantic's exclude_unset feature.
    Password updates are automatically hashed.
    
    Args:
        db: Database session for query execution.
        db_admin: Existing Admin object to update.
        admin_update: AdminUpdate schema with fields to update.
        
    Returns:
        Updated Admin object.
        
    Note:
        Only provided fields are updated. Password is hashed if included.
    """
    update_data = admin_update.model_dump(exclude_unset=True)
    # Special handling for password - hash before storing
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
    """Permanently delete an admin account.
    
    Args:
        db: Database session for query execution.
        admin_id: Unique identifier of the admin to delete.
        
    Returns:
        Deleted Admin object if found and deleted, None otherwise.
        
    Warning:
        This is a permanent deletion. Consider soft delete for production.
    """
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if db_admin:
        db.delete(db_admin)
        db.commit()
    return db_admin
