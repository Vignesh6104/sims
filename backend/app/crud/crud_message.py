from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.message import Message
from app.schemas.message import MessageCreate

def create_message(db: Session, message: MessageCreate, sender_id: str, sender_role: str, sender_name: str):
    db_message = Message(
        sender_id=sender_id,
        sender_role=sender_role,
        sender_name=sender_name,
        receiver_id=message.receiver_id,
        receiver_role=message.receiver_role,
        receiver_name=message.receiver_name,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_conversation(db: Session, user_a_id: str, user_b_id: str, limit: int = 50):
    return db.query(Message).filter(
        or_(
            and_(Message.sender_id == user_a_id, Message.receiver_id == user_b_id),
            and_(Message.sender_id == user_b_id, Message.receiver_id == user_a_id)
        )
    ).order_by(Message.created_at.asc()).limit(limit).all()

def get_user_messages(db: Session, user_id: str, limit: int = 100):
    return db.query(Message).filter(
        or_(Message.sender_id == user_id, Message.receiver_id == user_id)
    ).order_by(Message.created_at.desc()).limit(limit).all()
