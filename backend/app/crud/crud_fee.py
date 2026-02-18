"""CRUD operations for fee management.

This module handles fee structure definitions and payment tracking
for student financial records and accounting purposes.
"""

from sqlalchemy.orm import Session
from app.models.fee import FeeStructure, FeePayment
from app.schemas.fee import FeeStructureCreate, FeePaymentCreate


def get_fee_structures(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve all fee structures with pagination.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        
    Returns:
        List of FeeStructure objects.
    """
    return db.query(FeeStructure).offset(skip).limit(limit).all()


def create_fee_structure(db: Session, fee_in: FeeStructureCreate):
    """Create a new fee structure.
    
    Args:
        db: Database session for query execution.
        fee_in: FeeStructureCreate schema with fee details.
        
    Returns:
        Newly created FeeStructure object with generated ID.
    """
    db_fee = FeeStructure(**fee_in.model_dump())
    db.add(db_fee)
    db.commit()
    db.refresh(db_fee)
    return db_fee


def get_fee_payments_by_student(db: Session, student_id: str):
    """Retrieve all fee payments made by a specific student.
    
    Args:
        db: Database session for query execution.
        student_id: Unique identifier of the student.
        
    Returns:
        List of FeePayment objects for the specified student.
    """
    return db.query(FeePayment).filter(FeePayment.student_id == student_id).all()


def create_fee_payment(db: Session, payment_in: FeePaymentCreate):
    """Record a new fee payment.
    
    Args:
        db: Database session for query execution.
        payment_in: FeePaymentCreate schema with payment details.
        
    Returns:
        Newly created FeePayment object with generated ID.
    """
    db_payment = FeePayment(**payment_in.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment
