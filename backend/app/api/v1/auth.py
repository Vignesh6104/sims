from typing import Any
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter()

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