from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate

def create_notification(db: Session, notification: NotificationCreate):
    db_notification = Notification(**notification.model_dump())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_for_user(db: Session, user_id: str, role: str, skip: int = 0, limit: int = 100):
    # Fetch direct messages OR broadcasts to their role OR broadcasts to 'all'
    return db.query(Notification).filter(
        (Notification.recipient_id == user_id) | 
        (Notification.recipient_role == role) |
        (Notification.recipient_role == 'all')
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_notification_read(db: Session, notification_id: str):
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if db_notification:
        db_notification.is_read = True
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
    return db_notification
