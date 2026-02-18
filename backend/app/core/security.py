"""
Security and Authentication Module

This module provides core security functionality for the SIMS application, including:
- JWT token generation (access and refresh tokens)
- Password hashing and verification using bcrypt
- Token payload construction with unique identifiers

Token Structure:
    Both access and refresh tokens contain:
    - exp: Expiration timestamp (UTC)
    - sub: Subject (user ID)
    - type: Token type ("access" or "refresh")
    - jti: JWT ID (UUID4) for uniqueness and revocation tracking
    - role: User role (admin, teacher, student, parent)
    - full_name: User's display name (access tokens only)

Security Features:
    - Bcrypt password hashing with configurable work factor
    - Unique token identifiers (jti) to prevent token reuse
    - Separate access and refresh token lifecycles
    - Role-based payload inclusion for authorization

Usage:
    from app.core.security import create_access_token, verify_password
    
    # Hash a password
    hashed = get_password_hash("mypassword")
    
    # Verify a password
    is_valid = verify_password("mypassword", hashed)
    
    # Create tokens
    access_token = create_access_token(user_id, role="admin", full_name="John Doe")
    refresh_token = create_refresh_token(user_id, role="admin")
"""

import uuid
from datetime import datetime, timedelta, UTC
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context with bcrypt
# Rounds are configurable via BCRYPT_ROUNDS setting (default: 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)

# JWT algorithm - HS256 is symmetric signing with secret key
ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None, role: str = None, full_name: str = None) -> str:
    """
    Generate a new JWT access token.
    
    Inclusions:
    - exp: Expiration time
    - sub: User ID
    - type: 'access'
    - jti: Unique identifier to prevent duplicate tokens in same second
    - role: User role (admin, teacher, etc.)
    - full_name: Display name for immediate frontend use
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adding a unique identifier (jti) ensures tokens are unique 
    # even if generated in the same millisecond with same data
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "type": "access",
        "jti": str(uuid.uuid4()) 
    }
    if role:
        to_encode["role"] = role
    if full_name:
        to_encode["full_name"] = full_name
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], role: str = None) -> str:
    """
    Generate a long-lived JWT refresh token.
    Used to obtain new access tokens without requiring the user to re-login.
    """
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }
    if role:
        to_encode["role"] = role
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.
    
    Args:
        plain_password: The password to verify (user input)
        hashed_password: The stored bcrypt hash from database
    
    Returns:
        bool: True if password matches hash, False otherwise
    
    Example:
        is_valid = verify_password("user_input", user.hashed_password)
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a bcrypt hash for a plain text password.
    
    The number of rounds is determined by BCRYPT_ROUNDS setting.
    Higher rounds = more secure but slower (12 is recommended minimum).
    
    Args:
        password: Plain text password to hash
    
    Returns:
        str: Bcrypt hash string suitable for database storage
    
    Example:
        hashed = get_password_hash("newpassword123")
        user.hashed_password = hashed
    """
    return pwd_context.hash(password)
