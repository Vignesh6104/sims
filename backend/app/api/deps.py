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
from app.schemas.common import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> Union[Admin, Teacher, Student]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = None
    if token_data.role == "admin":
        user = db.query(Admin).filter(Admin.id == token_data.sub).first()
    elif token_data.role == "teacher":
        user = db.query(Teacher).filter(Teacher.id == token_data.sub).first()
    elif token_data.role == "student":
        user = db.query(Student).filter(Student.id == token_data.sub).first()
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: Union[Admin, Teacher, Student] = Depends(get_current_user),
) -> Union[Admin, Teacher, Student]:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: Union[Admin, Teacher, Student] = Depends(get_current_user),
) -> Admin:
    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

def get_current_active_staff(
    current_user: Union[Admin, Teacher, Student] = Depends(get_current_user),
) -> Union[Admin, Teacher]:
    if not isinstance(current_user, (Admin, Teacher)):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
