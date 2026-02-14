from sqlalchemy import Column, String, ForeignKey, Float, DateTime, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.db.session import Base

from app.models.fee import PaymentStatus
class Salary(Base):
    __tablename__ = "salaries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False, unique=True)
    
    base_salary = Column(Float, nullable=False)
    allowances = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    teacher = relationship("Teacher")

class PayrollRecord(Base):
    __tablename__ = "payroll_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False)
    
    month = Column(Integer, nullable=False) # 1-12
    year = Column(Integer, nullable=False)
    
    amount_paid = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus, name="payroll_status"), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    teacher = relationship("Teacher")
