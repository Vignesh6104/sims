from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_event
from app.schemas.event import Event, EventCreate

router = APIRouter()

@router.get("/", response_model=List[Event])
def read_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_event.get_events(db, skip=skip, limit=limit)

@router.post("/", response_model=Event)
def create_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: EventCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admins
) -> Any:
    return crud_event.create_event(db, event=event_in)

@router.delete("/{event_id}", response_model=Event)
def delete_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    event = crud_event.get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return crud_event.delete_event(db, event_id=event_id)