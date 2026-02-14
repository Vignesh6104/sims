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
    OAuth2 compatible token login, get an access token for future requests.
    Checks Admin, then Teacher, then Student, then Parent.
    """
    email = form_data.username
    password = form_data.password
    
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
    Refresh access token.
    """
    try:
        payload = jwt.decode(
            data.refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid or expired refresh token")
    
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
    Simulate forgot password. Returns a reset token.
    """
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
    Reset password using token.
    """
    try:
        payload = jwt.decode(
            data.token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
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
    Register a new student.
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
    Register a new teacher.
    """
    user = crud_teacher.get_teacher_by_email(db, email=teacher_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Teacher with this email already exists")
    return crud_teacher.create_teacher(db, teacher=teacher_in)