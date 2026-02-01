from sqlalchemy.orm import Session
from app.models.class_room import ClassRoom
from app.schemas.class_room import ClassRoomCreate, ClassRoomUpdate

def get_class_room(db: Session, class_room_id: str):
    return db.query(ClassRoom).filter(ClassRoom.id == class_room_id).first()

def get_class_room_by_name(db: Session, name: str):
    return db.query(ClassRoom).filter(ClassRoom.name == name).first()

def get_class_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ClassRoom).offset(skip).limit(limit).all()

def get_class_rooms_by_teacher(db: Session, teacher_id: str, skip: int = 0, limit: int = 100):
    return db.query(ClassRoom).filter(ClassRoom.teacher_id == teacher_id).offset(skip).limit(limit).all()

def create_class_room(db: Session, class_room: ClassRoomCreate):
    db_class_room = ClassRoom(name=class_room.name, teacher_id=class_room.teacher_id)
    db.add(db_class_room)
    db.commit()
    db.refresh(db_class_room)
    return db_class_room

def update_class_room(db: Session, db_class_room: ClassRoom, class_room_update: ClassRoomUpdate):
    update_data = class_room_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_class_room, key, value)
    db.add(db_class_room)
    db.commit()
    db.refresh(db_class_room)
    return db_class_room

def delete_class_room(db: Session, class_room_id: str):
    db_class_room = db.query(ClassRoom).filter(ClassRoom.id == class_room_id).first()
    if db_class_room:
        db.delete(db_class_room)
        db.commit()
    return db_class_room