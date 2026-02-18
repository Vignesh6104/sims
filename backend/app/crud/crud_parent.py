"""CRUD operations for Parent user management.

This module handles all database operations for parent/guardian accounts.
Parents can monitor their children's academic progress and communicate with teachers.
"""

from sqlalchemy.orm import Session
from app.models.parent import Parent
from app.schemas.parent import ParentCreate, ParentUpdate
from app.core.security import get_password_hash


def get_parent(db: Session, parent_id: str):
    """Retrieve a parent by their unique identifier.
    
    Args:
        db: Database session for query execution.
        parent_id: Unique identifier of the parent.
        
    Returns:
        Parent object if found, None otherwise.
    """
    return db.query(Parent).filter(Parent.id == parent_id).first()


def get_parent_by_email(db: Session, email: str):
    """Retrieve a parent by their email address.
    
    Used for authentication and duplicate checking.
    
    Args:
        db: Database session for query execution.
        email: Email address to search for.
        
    Returns:
        Parent object if found, None otherwise.
    """
    return db.query(Parent).filter(Parent.email == email).first()


def get_parents(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a paginated list of all parents.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of Parent objects.
    """
    return db.query(Parent).offset(skip).limit(limit).all()


def create_parent(db: Session, parent: ParentCreate):
    """Create a new parent account with hashed password.
    
    Args:
        db: Database session for query execution.
        parent: ParentCreate schema with parent details.
        
    Returns:
        Newly created Parent object with generated ID.
        
    Note:
        Password is automatically hashed before storage.
    """
    # Hash the password for secure storage
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
    """Update parent profile. Automatically hashes password if provided.
    
    Supports partial updates using Pydantic's exclude_unset feature.
    
    Args:
        db: Database session for query execution.
        db_parent: Existing Parent object to update.
        parent_update: ParentUpdate schema with fields to update.
        
    Returns:
        Updated Parent object.
        
    Note:
        Only provided fields are updated. Password is hashed if included.
    """
    update_data = parent_update.model_dump(exclude_unset=True)
    # Special handling for password updates
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
