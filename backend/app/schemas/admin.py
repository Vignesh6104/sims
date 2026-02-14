from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: Optional[bool] = True

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(AdminBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile_image: Optional[str] = None

class AdminInDBBase(AdminBase):
    id: str

    class Config:
        from_attributes = True

class Admin(AdminInDBBase):
    pass
