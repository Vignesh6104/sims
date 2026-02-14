from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.asset import Asset

router = APIRouter()

@router.get("/")
def read_assets(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
):
    return db.query(Asset).all()
