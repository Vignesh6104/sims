from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.models.fee import PaymentStatus

# Fee Structure Schemas
class FeeStructureBase(BaseModel):
    class_id: str
    academic_year: str
    amount: float
    description: Optional[str] = None
    due_date: date

class FeeStructureCreate(FeeStructureBase):
    pass

class FeeStructureUpdate(FeeStructureBase):
    pass

class FeeStructureInDBBase(FeeStructureBase):
    id: str

    class Config:
        from_attributes = True

class FeeStructure(FeeStructureInDBBase):
    pass

# Fee Payment Schemas
class FeePaymentBase(BaseModel):
    amount_paid: float
    payment_date: date
    status: PaymentStatus = PaymentStatus.PAID
    remarks: Optional[str] = None

class FeePaymentCreate(FeePaymentBase):
    student_id: str
    fee_structure_id: str

class FeePaymentUpdate(FeePaymentBase):
    pass

class FeePaymentInDBBase(FeePaymentBase):
    id: str
    student_id: str
    fee_structure_id: str

    class Config:
        from_attributes = True

class FeePayment(FeePaymentInDBBase):
    pass
