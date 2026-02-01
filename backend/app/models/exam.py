import uuid
from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship
from app.db.session import Base

class Exam(Base):
    __tablename__ = "exams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False) 
    date = Column(Date, nullable=False)
    
    marks = relationship("Mark", back_populates="exam")