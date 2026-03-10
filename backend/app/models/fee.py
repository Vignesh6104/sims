"""Fee structure and payment models for the School Information Management System.

This module defines the FeeStructure and FeePayment models for managing student
tuition fees, payment tracking, and financial records.
"""
import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class PaymentStatus(str, enum.Enum):
    """Enumeration of possible payment statuses.
    
    Values:
        PENDING: Fee is due but not yet paid.
        PARTIAL: Some amount has been paid, but not the full fee.
        PAID: Full fee amount has been paid.
        OVERDUE: Payment deadline has passed without full payment.
    """
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"

class FeeStructure(Base):
    """Represents a fee structure for a specific class and academic year.
    
    Fee structures define:
    - Fee amounts for different classes
    - Academic year-based fee schedules
    - Payment deadlines
    - Fee categories (tuition, lab fees, etc.)
    
    Relationships:
        classroom: Many-to-one relationship with ClassRoom (fee structure is for a specific class).
    
    Attributes:
        id (str): Unique identifier (UUID) for the fee structure.
        class_id (str): Foreign key linking to the class this fee applies to.
        academic_year (str): Academic year for this fee (e.g., "2024-2025").
        amount (float): Total fee amount for the period.
        description (str): Optional description of fee type (e.g., "Tuition Fee", "Lab Fee").
        due_date (date): Deadline for fee payment.
    """
    __tablename__ = "fee_structures"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    academic_year = Column(String, nullable=False)  # e.g., "2024-2025"
    amount = Column(Float, nullable=False)  # Total fee amount
    description = Column(String, nullable=True)  # e.g., "Tuition Fee", "Lab Fee", "Sports Fee"
    due_date = Column(Date, nullable=False)  # Payment deadline

    # Relationship for accessing class information
    classroom = relationship("ClassRoom")

class FeePayment(Base):
    """Represents a fee payment record for a student.
    
    Fee payments track:
    - Student payment history
    - Partial and full payments
    - Payment dates and status
    - Outstanding balances
    
    Relationships:
        student: Many-to-one relationship with Student (payment belongs to a specific student).
        fee_structure: Many-to-one relationship with FeeStructure (payment is for a specific fee).
    
    Attributes:
        id (str): Unique identifier (UUID) for the payment record.
        student_id (str): Foreign key linking to the student making the payment.
        fee_structure_id (str): Foreign key linking to the applicable fee structure.
        amount_paid (float): Amount actually paid by the student (can be partial).
        payment_date (date): Date when the payment was made (null if pending).
        status (PaymentStatus): Current payment status (pending/partial/paid/overdue).
        remarks (str): Optional notes about the payment (e.g., "Scholarship applied").
    """
    __tablename__ = "fee_payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    fee_structure_id = Column(String, ForeignKey("fee_structures.id"), nullable=False)
    amount_paid = Column(Float, default=0.0)  # Amount paid (can be partial)
    payment_date = Column(Date, nullable=True)  # Null until payment is made
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    remarks = Column(String, nullable=True)  # Optional notes (e.g., "Late payment", "Scholarship")

    # Relationships for accessing payment context
    student = relationship("Student")
    fee_structure = relationship("FeeStructure")
