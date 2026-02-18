"""School asset management model for the School Information Management System.

This module defines the Asset model for tracking and managing school property,
equipment, and physical resources.
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

class Asset(Base):
    """Represents a physical asset or equipment owned by the school.
    
    Asset management is used to:
    - Track school property and equipment
    - Monitor asset location and condition
    - Maintain inventory of resources
    - Schedule maintenance and repairs
    - Record purchase history
    
    Examples of assets:
    - Lab equipment (microscopes, beakers, etc.)
    - Computer hardware and IT equipment
    - Sports equipment
    - Furniture and fixtures
    - Library furniture
    - Musical instruments
    
    Attributes:
        id (str): Unique identifier (UUID) for the asset.
        name (str): Name or title of the asset (e.g., "Digital Microscope", "Dell Laptop").
        category (str): Asset category (e.g., "Lab Equipment", "Computer", "Sports", "Furniture").
        quantity (int): Number of units of this asset (default: 1).
        description (str): Detailed description, specifications, or notes about the asset.
        location (str): Physical location of the asset (e.g., "Physics Lab", "Room 302", "Library").
        purchase_date (datetime): Date when the asset was purchased (optional).
        status (str): Current condition of the asset (default: "Functional").
                     Common values: "Functional", "Broken", "Under Maintenance", "Retired".
        created_at (datetime): Timestamp when asset record was created.
        updated_at (datetime): Timestamp when asset record was last updated.
    """
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # Asset name
    category = Column(String, nullable=False)  # Category (e.g., "Lab Equipment", "Computer", "Sports")
    quantity = Column(Integer, default=1)  # Number of units
    description = Column(Text, nullable=True)  # Detailed description or specifications
    location = Column(String, nullable=True)  # Physical location (e.g., "Physics Lab", "Room 302")
    
    purchase_date = Column(DateTime, nullable=True)  # Purchase date for warranty/depreciation tracking
    status = Column(String, default="Functional")  # Condition: "Functional", "Broken", "Maintenance", etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
