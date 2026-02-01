from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_fee
from app.schemas.fee import FeeStructure, FeeStructureCreate, FeePayment, FeePaymentCreate

router = APIRouter()

@router.get("/structures", response_model=List[FeeStructure])
def read_fee_structures(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    return crud_fee.get_fee_structures(db, skip=skip, limit=limit)

@router.post("/structures", response_model=FeeStructure)
def create_fee_structure(
    *,
    db: Session = Depends(deps.get_db),
    fee_in: FeeStructureCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    return crud_fee.create_fee_structure(db, fee_in=fee_in)

@router.get("/payments/student/{student_id}", response_model=List[FeePayment])
def read_student_payments(
    student_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_fee.get_fee_payments_by_student(db, student_id=student_id)

@router.post("/payments", response_model=FeePayment)
def create_payment(
    *,
    db: Session = Depends(deps.get_db),
    payment_in: FeePaymentCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin records payments
) -> Any:
    return crud_fee.create_fee_payment(db, payment_in=payment_in)
