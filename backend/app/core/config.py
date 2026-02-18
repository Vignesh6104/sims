"""
Application Configuration Module

This module defines the central configuration settings for the SIMS backend application
using Pydantic Settings for type-safe environment variable management. All settings are
loaded from the .env file and validated at startup.

Configuration Categories:
    - Project metadata (name, API version, CORS origins)
    - Database connection settings
    - Security parameters (JWT, password hashing)
    - External service credentials (Cloudinary for file storage)

Environment Variables Required:
    PROJECT_NAME: Application display name
    API_V1_STR: API version prefix (e.g., "/api/v1")
    SQLALCHEMY_DATABASE_URI: Database connection string
    SECRET_KEY: JWT signing secret (keep secure!)
    ALGORITHM: JWT algorithm (e.g., "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: Access token lifetime
    REFRESH_TOKEN_EXPIRE_DAYS: Refresh token lifetime
    CLOUDINARY_CLOUD_NAME: Cloudinary account name
    CLOUDINARY_API_KEY: Cloudinary API key
    CLOUDINARY_API_SECRET: Cloudinary API secret

Optional:
    FRONTEND_URL: CORS origin (default: "http://localhost:5173")
    BCRYPT_ROUNDS: Password hashing cost factor (default: 12)

Usage:
    from app.core.config import settings
    database_url = settings.SQLALCHEMY_DATABASE_URI
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Main application settings loaded from environment variables.
    
    All settings are validated at startup. Missing required variables will
    cause the application to fail fast with a clear error message.
    
    Attributes:
        PROJECT_NAME (str): Display name for the application
        API_V1_STR (str): API version prefix for routing
        FRONTEND_URL (str): Allowed CORS origin for frontend
        SQLALCHEMY_DATABASE_URI (str): SQLAlchemy-compatible database URL
        SECRET_KEY (str): Cryptographic secret for JWT signing
        ALGORITHM (str): JWT signing algorithm (HS256 recommended)
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Access token TTL in minutes
        REFRESH_TOKEN_EXPIRE_DAYS (int): Refresh token TTL in days
        BCRYPT_ROUNDS (int): Bcrypt hashing cost factor (higher = more secure but slower)
        CLOUDINARY_CLOUD_NAME (str): Cloudinary account identifier
        CLOUDINARY_API_KEY (str): Cloudinary API authentication key
        CLOUDINARY_API_SECRET (str): Cloudinary API authentication secret
    """
    PROJECT_NAME: str
    API_V1_STR: str
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Database
    SQLALCHEMY_DATABASE_URI: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    BCRYPT_ROUNDS: int = 12 # Default bcrypt rounds

    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:
        """Pydantic configuration for settings validation."""
        case_sensitive = True
        env_file = ".env"

# Global settings instance - import this singleton throughout the application
settings = Settings()
