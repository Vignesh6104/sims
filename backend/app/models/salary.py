"""Salary and payroll models for the School Information Management System.

This module defines the Salary and PayrollRecord models for managing teacher
compensation, payroll processing, and salary disbursement tracking.
"""
from sqlalchemy import Column, String, ForeignKey, Float, DateTime, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.db.session import Base

from app.models.fee import PaymentStatus

class Salary(Base):
    """Represents the salary structure for a teacher.
    
    Salary records define:
    - Base salary amounts
    - Allowances (housing, travel, etc.)
    - Deductions (taxes, advances, etc.)
    - Net salary calculations
    
    Note: Each teacher can have only one active salary record (unique constraint).
    
    Relationships:
        teacher: One-to-one relationship with Teacher (each teacher has one salary record).
    
    Attributes:
        id (str): Unique identifier (UUID) for the salary record.
        teacher_id (str): Foreign key linking to the teacher (unique - one salary per teacher).
        base_salary (float): Base monthly salary amount.
        allowances (float): Additional allowances (housing, travel, etc.).
        deductions (float): Deductions (taxes, provident fund, etc.).
        created_at (datetime): Timestamp when the salary record was created.
        updated_at (datetime): Timestamp when the salary was last updated.
    """
    __tablename__ = "salaries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False, unique=True)  # One salary per teacher
    
    base_salary = Column(Float, nullable=False)  # Base monthly salary
    allowances = Column(Float, default=0.0)  # Additional allowances (housing, travel, etc.)
    deductions = Column(Float, default=0.0)  # Deductions (taxes, PF, loans, etc.)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship for accessing teacher information
    teacher = relationship("Teacher")

class PayrollRecord(Base):
    """Represents a monthly payroll payment record for a teacher.
    
    Payroll records track:
    - Monthly salary disbursements
    - Payment status and dates
    - Historical payment records
    - Pending and completed payments
    
    Relationships:
        teacher: Many-to-one relationship with Teacher (multiple monthly records per teacher).
    
    Attributes:
        id (str): Unique identifier (UUID) for the payroll record.
        teacher_id (str): Foreign key linking to the teacher receiving payment.
        month (int): Month of payment (1-12).
        year (int): Year of payment (e.g., 2024).
        amount_paid (float): Actual amount disbursed (after allowances and deductions).
        status (PaymentStatus): Payment status (pending/paid) - reuses enum from fee module.
        payment_date (datetime): Date when payment was processed (null if pending).
        created_at (datetime): Timestamp when the payroll record was created.
    """
    __tablename__ = "payroll_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False)
    
    month = Column(Integer, nullable=False)  # 1-12 representing January-December
    year = Column(Integer, nullable=False)  # Year of payment (e.g., 2024)
    
    amount_paid = Column(Float, nullable=False)  # Actual disbursed amount
    status = Column(Enum(PaymentStatus, name="payroll_status"), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime(timezone=True), nullable=True)  # Null until paid
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship for accessing teacher information
    teacher = relationship("Teacher")
