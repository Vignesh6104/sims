import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Admin specific fields
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
