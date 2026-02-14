from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    category = Column(String, nullable=False) # e.g., "Lab Equipment", "Computer", "Sports"
    quantity = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True) # e.g., "Physics Lab", "Room 302"
    
    purchase_date = Column(DateTime, nullable=True)
    status = Column(String, default="Functional") # e.g., "Functional", "Broken", "Maintenance"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
