"""Admin user model for the School Information Management System.

This module defines the Admin model representing administrative staff who have
full access to the SIMS platform with elevated privileges for managing all aspects
of the school system.
"""
import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class Admin(Base):
    """Represents an administrative user in the school management system.
    
    Admins have the highest level of access and are responsible for:
    - Managing all users (teachers, students, parents)
    - Configuring system settings
    - Overseeing academic operations
    - Managing financial records
    - Generating reports and analytics
    
    Attributes:
        id (str): Unique identifier (UUID) for the admin.
        email (str): Unique email address used for authentication.
        hashed_password (str): Securely hashed password for authentication.
        full_name (str): Full name of the admin.
        is_active (bool): Account status; False indicates deactivated account.
        department (str): Department the admin belongs to (e.g., "Administration", "IT").
        position (str): Job title or position (e.g., "Principal", "Vice Principal").
        profile_image (str): URL or path to the admin's profile image.
    """
    __tablename__ = "admins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)  # Indexed for fast login lookups
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)  # Used to disable accounts without deletion
    
    # Admin-specific fields
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)  # Stores file path or URL
