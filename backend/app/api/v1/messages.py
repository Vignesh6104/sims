from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.message import Message, MessageCreate
from app.crud import crud_message

router = APIRouter()

@router.post("/", response_model=Message)
def send_message(
    message_in: MessageCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    # Identify sender role
    role = current_user.__class__.__name__.lower()
    name = getattr(current_user, "full_name", "Unknown")
    
    return crud_message.create_message(
        db=db, 
        message=message_in, 
        sender_id=str(current_user.id), 
        sender_role=role,
        sender_name=name
    )

@router.get("/", response_model=List[Message])
def read_messages(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_message.get_user_messages(db, user_id=str(current_user.id))

@router.get("/conversation/{other_user_id}", response_model=List[Message])
def read_conversation(
    other_user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_message.get_conversation(db, user_a_id=str(current_user.id), user_b_id=other_user_id)
