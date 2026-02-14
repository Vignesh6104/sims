from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.salary import Salary, PayrollRecord

router = APIRouter()

@router.get("/salaries")
def read_salaries(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
):
    return db.query(Salary).all()

@router.get("/payroll")
def read_payroll(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
):
    return db.query(PayrollRecord).all()
