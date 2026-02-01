from sqlalchemy.orm import Session
from app.models.fee import FeeStructure, FeePayment
from app.schemas.fee import FeeStructureCreate, FeePaymentCreate

def get_fee_structures(db: Session, skip: int = 0, limit: int = 100):
    return db.query(FeeStructure).offset(skip).limit(limit).all()

def create_fee_structure(db: Session, fee_in: FeeStructureCreate):
    db_fee = FeeStructure(**fee_in.model_dump())
    db.add(db_fee)
    db.commit()
    db.refresh(db_fee)
    return db_fee

def get_fee_payments_by_student(db: Session, student_id: str):
    return db.query(FeePayment).filter(FeePayment.student_id == student_id).all()

def create_fee_payment(db: Session, payment_in: FeePaymentCreate):
    db_payment = FeePayment(**payment_in.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment
