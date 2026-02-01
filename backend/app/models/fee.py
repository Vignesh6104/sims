import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"

class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String, ForeignKey("classrooms.id"), nullable=False)
    academic_year = Column(String, nullable=False) # e.g., "2024-2025"
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True) # e.g., "Tuition Fee"
    due_date = Column(Date, nullable=False)

    classroom = relationship("ClassRoom")

class FeePayment(Base):
    __tablename__ = "fee_payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    fee_structure_id = Column(String, ForeignKey("fee_structures.id"), nullable=False)
    amount_paid = Column(Float, default=0.0)
    payment_date = Column(Date, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    remarks = Column(String, nullable=True)

    student = relationship("Student")
    fee_structure = relationship("FeeStructure")
