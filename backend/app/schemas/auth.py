from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class WebAuthnRegistrationVerifyRequest(BaseModel):
    credential: dict

class WebAuthnLoginOptionsRequest(BaseModel):
    email: EmailStr

class WebAuthnLoginVerifyRequest(BaseModel):
    email: EmailStr
    credential: dict
