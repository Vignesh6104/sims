import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Parent(Base):
    __tablename__ = "parents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Simple 1-to-many: One parent can have multiple students (children)
    # But for simplicity in this MVP, let's link a parent to a student via the Student model
    # OR better: A Link table or foreign key on Student.
    # Let's put a foreign key on Student to Parent? No, a student has parents.
    # Let's put a Parent ID on Student for simplicity (Single parent system for now)
    # OR: A parent has a list of student_ids.
    
    # Approach: One Parent -> Many Students.
    # We will add `parent_id` to Student model in a migration.
    
    students = relationship("Student", back_populates="parent")
