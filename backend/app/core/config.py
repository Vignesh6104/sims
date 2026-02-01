from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str
    
    # Database
    SQLALCHEMY_DATABASE_URI: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    BCRYPT_ROUNDS: int = 12 # Default bcrypt rounds

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
