"""
Authentication and User Management API Endpoints.

This module provides comprehensive authentication and user profile management
endpoints for the School Information Management System (SIMS). It handles:
- OAuth2-based login/logout with JWT tokens
- Token refresh mechanism
- Password reset functionality
- User registration (students and teachers)
- Profile management (view/update profile and profile images)

Authentication Method:
    OAuth2 with Password Flow (Bearer tokens)
    - Access tokens expire based on ACCESS_TOKEN_EXPIRE_MINUTES setting
    - Refresh tokens are long-lived and can generate new access tokens

Supported User Roles:
    - Admin: System administrators with full access
    - Teacher: Teaching staff with class management access
    - Student: Enrolled students with limited access
    - Parent: Parents/guardians with read access to children's data

Security:
    - Passwords are hashed using bcrypt
    - JWT tokens signed with SECRET_KEY
    - Profile images uploaded to Cloudinary
"""
from typing import Any, Union
from datetime import timedelta
import os
import tempfile
import shutil
import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import crud_student, crud_teacher, crud_admin, crud_parent
from app.schemas.auth import Token, ForgotPassword, ResetPassword, TokenPayload, RefreshTokenRequest
from app.schemas.student import Student as StudentSchema, StudentCreate
from app.schemas.teacher import Teacher as TeacherSchema, TeacherCreate
from app.models.admin import Admin
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.parent import Parent

from app.schemas.admin import Admin as AdminSchema, AdminUpdate
from app.schemas.parent import Parent as ParentSchema, ParentUpdate

router = APIRouter()

# Combine schemas for polymorphic response
UserSchema = Union[AdminSchema, TeacherSchema, StudentSchema, ParentSchema]

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve the profile information of the currently authenticated user.
    
    Args:
        current_user: The authenticated user object injected by the security dependency.
        
    Returns:
        The user object (Admin, Teacher, Student, or Parent) matching the current session.
    """
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: Any = Body(...),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update the profile information for the currently authenticated user.
    Handles dynamic role detection to update the correct database table.
    
    Args:
        db: Database session.
        user_in: Dictionary or schema containing the fields to update.
        current_user: The authenticated user object.
        
    Returns:
        The updated user object.
        
    Raises:
        HTTPException: If the user type is invalid.
    """
    update_data = user_in if isinstance(user_in, dict) else user_in.dict(exclude_unset=True)
    
    if isinstance(current_user, Admin):
        from app.crud import crud_admin
        return crud_admin.update_admin(db, db_admin=current_user, admin_update=AdminUpdate(**update_data))
    
    elif isinstance(current_user, Teacher):
        from app.crud import crud_teacher
        return crud_teacher.update_teacher(db, db_teacher=current_user, teacher_update=TeacherUpdate(**update_data))
    
    elif isinstance(current_user, Student):
        from app.crud import crud_student
        from app.schemas.student import StudentUpdate
        return crud_student.update_student(db, db_student=current_user, student_update=StudentUpdate(**update_data))
    
    elif isinstance(current_user, Parent):
        from app.crud import crud_parent
        return crud_parent.update_parent(db, db_parent=current_user, parent_update=ParentUpdate(**update_data))

    raise HTTPException(status_code=400, detail="Invalid user type")

@router.put("/me/profile-image", response_model=UserSchema)
async def update_profile_image(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload and update the profile image for the currently authenticated user.
    The image is uploaded to Cloudinary, and the secure URL is saved to the database.
    
    Args:
        db: Database session.
        file: The image file uploaded via multipart form data.
        current_user: The authenticated user object.
        
    Returns:
        The user object with the updated profile_image URL.
        
    Raises:
        HTTPException: If Cloudinary upload fails.
    """
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            
        upload_result = cloudinary.uploader.upload(
            temp_file_path, 
            folder="sims_profiles",
            resource_type="image"
        )
        file_url = upload_result.get("secure_url") or upload_result.get("url")
        if not file_url:
            raise HTTPException(status_code=500, detail="Cloudinary upload failed")
            
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    current_user.profile_image = file_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login for all user types.
    
    Authenticates a user and returns JWT access and refresh tokens.
    Searches for the user across all role tables (Admin, Teacher, Student, Parent)
    in sequence until a match is found.
    
    Request Body (Form Data):
        username: User's email address
        password: Plain text password (will be verified against hashed password)
        
    Returns:
        Token: Contains access_token, refresh_token, and token_type
        - access_token: Short-lived JWT for API authentication
        - refresh_token: Long-lived JWT for obtaining new access tokens
        - token_type: Always "bearer"
        
    Raises:
        HTTPException 400: Invalid credentials or inactive user account
        
    Example:
        POST /api/v1/auth/login
        Content-Type: application/x-www-form-urlencoded
        
        username=teacher@school.com&password=secret123
    """
    email = form_data.username
    password = form_data.password
    
    # Search for user across all role tables in priority order
    user = crud_admin.get_admin_by_email(db, email=email)
    role = "admin"
    
    if not user:
        user = crud_teacher.get_teacher_by_email(db, email=email)
        role = "teacher"
    
    if not user:
        user = crud_student.get_student_by_email(db, email=email)
        role = "student"

    if not user:
        user = crud_parent.get_parent_by_email(db, email=email)
        role = "parent"

    # Validate credentials
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires, role=role, full_name=user.full_name
        ),
        "refresh_token": security.create_refresh_token(user.id, role=role),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    *,
    db: Session = Depends(deps.get_db),
    data: RefreshTokenRequest,
) -> Any:
    """
    Refresh access token using a valid refresh token.
    
    Allows clients to obtain a new access token without re-authenticating
    when the access token expires. The refresh token must be valid and
    the associated user account must still be active.
    
    Request Body:
        refresh_token (str): The refresh token obtained during login
        
    Returns:
        Token: New access token and the same refresh token
        
    Raises:
        HTTPException 400: Invalid token type, expired, or malformed token
        HTTPException 404: User not found in database
        HTTPException 400: User account is inactive
        
    Security Notes:
        - Validates token type is "refresh" (not an access token)
        - Verifies token signature and expiration
        - Checks user still exists and is active
    """
    try:
        # Decode and validate the refresh token
        payload = jwt.decode(
            data.refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid or expired refresh token")
    
    # Retrieve user based on role in token
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
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires, role=token_data.role, full_name=user.full_name
        ),
        "refresh_token": data.refresh_token, # Keep same refresh token or rotate
        "token_type": "bearer",
    }

@router.post("/forgot-password")
def forgot_password(
    *,
    db: Session = Depends(deps.get_db),
    data: ForgotPassword,
) -> Any:
    """
    Initiate password reset process.
    
    Generates a short-lived reset token that can be used to reset the password.
    In production, this token should be sent via email. For this implementation,
    it's returned directly in the response.
    
    Request Body:
        email (str): User's registered email address
        
    Returns:
        dict: Message and reset token (15-minute expiration)
        
    Raises:
        HTTPException 404: No user found with the provided email
        
    Security Notes:
        - Token expires in 15 minutes
        - Token contains user ID and role
        - In production, send token via email instead of response
    """
    # Search for user across all role tables
    user = crud_admin.get_admin_by_email(db, email=data.email)
    role = "admin"
    if not user:
        user = crud_teacher.get_teacher_by_email(db, email=data.email)
        role = "teacher"
    if not user:
        user = crud_student.get_student_by_email(db, email=data.email)
        role = "student"
    if not user:
        user = crud_parent.get_parent_by_email(db, email=data.email)
        role = "parent"
    
    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")
    
    # Generate short-lived reset token (15 minutes)
    reset_token = security.create_access_token(
        user.id, expires_delta=timedelta(minutes=15), role=role
    )
    
    return {"msg": "Password reset token generated", "token": reset_token}

@router.post("/reset-password")
def reset_password(
    *,
    db: Session = Depends(deps.get_db),
    data: ResetPassword,
) -> Any:
    """
    Reset user password using a valid reset token.
    
    Validates the reset token and updates the user's password.
    The token must be obtained from the /forgot-password endpoint.
    
    Request Body:
        token (str): Reset token from forgot-password endpoint
        new_password (str): New password (will be hashed before storage)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 400: Invalid or expired token
        HTTPException 404: User not found (may have been deleted)
        
    Security Notes:
        - Password is hashed using bcrypt before storage
        - Token is validated for signature and expiration
        - Old password is immediately invalidated
    """
    try:
        # Decode and validate reset token
        payload = jwt.decode(
            data.token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Retrieve user based on role in token
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
    
    # Update password with hashed version
    user.hashed_password = security.get_password_hash(data.new_password)
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}

@router.post("/register/student", response_model=StudentSchema)
def register_student(
    *,
    db: Session = Depends(deps.get_db),
    student_in: StudentCreate,
) -> Any:
    """
    Register a new student account (public endpoint).
    
    Allows self-registration of student accounts. Validates that the
    email is not already registered before creating the account.
    
    Request Body:
        StudentCreate schema containing:
        - email (str): Unique email address
        - password (str): Plain text password (will be hashed)
        - full_name (str): Student's full name
        - roll_number (str, optional): Student roll/ID number
        - date_of_birth (date, optional): Date of birth
        - address (str, optional): Residential address
        - class_id (str, optional): Initial class assignment
        
    Returns:
        Student: The newly created student object
        
    Raises:
        HTTPException 400: Email already registered
        
    HTTP Status Codes:
        200: Student successfully registered
        400: Duplicate email
    """
    user = crud_student.get_student_by_email(db, email=student_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Student with this email already exists")
    return crud_student.create_student(db, student=student_in)

@router.post("/register/teacher", response_model=TeacherSchema)
def register_teacher(
    *,
    db: Session = Depends(deps.get_db),
    teacher_in: TeacherCreate,
) -> Any:
    """
    Register a new teacher account (public endpoint).
    
    Allows self-registration of teacher accounts. Validates that the
    email is not already registered before creating the account.
    
    Request Body:
        TeacherCreate schema containing:
        - email (str): Unique email address
        - password (str): Plain text password (will be hashed)
        - full_name (str): Teacher's full name
        - qualification (str, optional): Educational qualifications
        - phone (str, optional): Contact number
        - address (str, optional): Residential address
        - subject_specialization (str, optional): Primary subject
        
    Returns:
        Teacher: The newly created teacher object
        
    Raises:
        HTTPException 400: Email already registered
        
    HTTP Status Codes:
        200: Teacher successfully registered
        400: Duplicate email
    """
    user = crud_teacher.get_teacher_by_email(db, email=teacher_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Teacher with this email already exists")
    return crud_teacher.create_teacher(db, teacher=teacher_in)