"""
FastAPI Dependency Injection Module

This module provides dependency injection functions for FastAPI endpoints, handling:
- Database session lifecycle management
- JWT authentication and validation
- User retrieval and authorization
- Role-based access control

Dependencies Available:
    get_db: Provides database session with automatic cleanup
    get_current_user: Extracts and validates JWT, returns authenticated user
    get_current_active_user: Ensures user account is active
    get_current_active_superuser: Restricts access to admin users only
    get_current_active_staff: Restricts access to admin and teacher users

Authentication Flow:
    1. OAuth2PasswordBearer extracts token from Authorization header
    2. JWT is decoded and validated
    3. Token payload is parsed into TokenPayload schema
    4. User is queried from database based on role and ID
    5. User object is returned for use in endpoint

Usage in FastAPI Endpoints:
    @router.get("/protected")
    def protected_route(
        db: Session = Depends(get_db),
        current_user: Union[Admin, Teacher, Student, Parent] = Depends(get_current_user)
    ):
        return {"user_id": current_user.id}
    
    @router.post("/admin-only")
    def admin_route(
        admin: Admin = Depends(get_current_active_superuser)
    ):
        return {"message": "Admin access granted"}
"""

from typing import Generator, Union, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.admin import Admin
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.parent import Parent
from app.schemas.common import TokenPayload

# OAuth2 scheme for extracting Bearer token from Authorization header
# Swagger UI uses this to display the login endpoint
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator:
    """
    Provide a database session for FastAPI endpoints.
    
    Creates a new SQLAlchemy session and ensures it's properly closed
    after the request completes, even if an exception occurs.
    
    Yields:
        Session: SQLAlchemy database session
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> Union[Admin, Teacher, Student, Parent]:
    """
    Authenticate user from JWT token and return user object.
    
    Extracts the JWT from the Authorization header, validates it, decodes the payload,
    and retrieves the corresponding user from the database based on role and ID.
    
    Args:
        db: Database session (injected)
        token: JWT access token from Authorization header (injected)
    
    Returns:
        Union[Admin, Teacher, Student, Parent]: Authenticated user object
    
    Raises:
        HTTPException 401: If token is invalid, expired, or malformed
        HTTPException 404: If user referenced in token doesn't exist in database
    
    Token Payload Structure:
        {
            "sub": "user_id",
            "role": "admin|teacher|student|parent",
            "exp": timestamp,
            "jti": "unique_token_id"
        }
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = None
    if token_data.role == "admin":
        user = db.query(Admin).filter(Admin.id == token_data.sub).first()
    elif token_data.role == "teacher":
        user = db.query(Teacher).filter(Teacher.id == token_data.sub).first()
    elif token_data.role == "student":
        user = db.query(Student).filter(Student.id == token_data.sub).first()
    elif token_data.role == "parent":
        user = db.query(Parent).filter(Parent.id == token_data.sub).first()
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: Union[Admin, Teacher, Student, Parent] = Depends(get_current_user),
) -> Union[Admin, Teacher, Student, Parent]:
    """
    Ensure the authenticated user has an active account.
    
    Builds on get_current_user by adding an additional check that the
    user's is_active flag is True. Inactive accounts cannot access endpoints.
    
    Args:
        current_user: Authenticated user from get_current_user (injected)
    
    Returns:
        Union[Admin, Teacher, Student, Parent]: Active user object
    
    Raises:
        HTTPException 400: If user account is inactive
    
    Usage:
        Recommended for all protected endpoints to prevent deactivated
        users from accessing the system.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: Union[Admin, Teacher, Student, Parent] = Depends(get_current_user),
) -> Admin:
    """
    Restrict endpoint access to admin users only.
    
    Validates that the authenticated user is an instance of the Admin model.
    This is used for administrative endpoints that should not be accessible
    to teachers, students, or parents.
    
    Args:
        current_user: Authenticated user from get_current_user (injected)
    
    Returns:
        Admin: Authenticated admin user
    
    Raises:
        HTTPException 400: If user is not an admin
    
    Usage:
        @router.delete("/users/{user_id}")
        def delete_user(admin: Admin = Depends(get_current_active_superuser)):
            # Only admins can delete users
    """
    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

def get_current_active_staff(
    current_user: Union[Admin, Teacher, Student, Parent] = Depends(get_current_user),
) -> Union[Admin, Teacher]:
    """
    Restrict endpoint access to staff members (admins and teachers).
    
    Validates that the authenticated user is either an Admin or Teacher.
    This is used for endpoints that require staff privileges but don't
    need full admin access (e.g., grading, attendance marking).
    
    Args:
        current_user: Authenticated user from get_current_user (injected)
    
    Returns:
        Union[Admin, Teacher]: Authenticated staff member
    
    Raises:
        HTTPException 400: If user is a student or parent
    
    Usage:
        @router.post("/attendance")
        def mark_attendance(staff: Union[Admin, Teacher] = Depends(get_current_active_staff)):
            # Only staff can mark attendance
    """
    if not isinstance(current_user, (Admin, Teacher)):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
