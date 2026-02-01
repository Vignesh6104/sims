from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_class_room
from app.schemas.class_room import ClassRoom, ClassRoomCreate, ClassRoomUpdate

router = APIRouter()

@router.get("/", response_model=List[ClassRoom])
def read_class_rooms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    teacher_id: Optional[str] = Query(None, description="Filter by Teacher ID"),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve class rooms. Optionally filter by teacher_id.
    """
    if teacher_id:
        return crud_class_room.get_class_rooms_by_teacher(db, teacher_id=teacher_id, skip=skip, limit=limit)
    return crud_class_room.get_class_rooms(db, skip=skip, limit=limit)

@router.post("/", response_model=ClassRoom)
def create_class_room(
    *,
    db: Session = Depends(deps.get_db),
    class_room_in: ClassRoomCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Create new class room.
    """
    class_room = crud_class_room.get_class_room_by_name(db, name=class_room_in.name)
    if class_room:
        raise HTTPException(status_code=400, detail="Class room with this name already exists")
    return crud_class_room.create_class_room(db, class_room=class_room_in)

@router.get("/{class_id}", response_model=ClassRoom)
def read_class_room(
    class_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get class room by ID.
    """
    class_room = crud_class_room.get_class_room(db, class_room_id=class_id)
    if not class_room:
        raise HTTPException(status_code=404, detail="Class room not found")
    return class_room

@router.put("/{class_id}", response_model=ClassRoom)
def update_class_room(
    *,
    db: Session = Depends(deps.get_db),
    class_id: str,
    class_room_in: ClassRoomUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Update class room.
    """
    class_room = crud_class_room.get_class_room(db, class_room_id=class_id)
    if not class_room:
        raise HTTPException(status_code=404, detail="Class room not found")
    return crud_class_room.update_class_room(db, db_class_room=class_room, class_room_update=class_room_in)

@router.delete("/{class_id}", response_model=ClassRoom)
def delete_class_room(
    *,
    db: Session = Depends(deps.get_db),
    class_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """
    Delete class room.
    """
    class_room = crud_class_room.get_class_room(db, class_room_id=class_id)
    if not class_room:
        raise HTTPException(status_code=404, detail="Class room not found")
    return crud_class_room.delete_class_room(db, class_room_id=class_id)