from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_library
from app.schemas.library import Book, BookCreate, BorrowRecord, BorrowCreate

router = APIRouter()

@router.get("/books", response_model=List[Book])
def read_books(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    return crud_library.get_books(db, skip=skip, limit=limit, search=search)

@router.post("/books", response_model=Book)
def create_book(
    *,
    db: Session = Depends(deps.get_db),
    book_in: BookCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin only
) -> Any:
    return crud_library.create_book(db, book=book_in)

@router.post("/issue", response_model=BorrowRecord)
def issue_book(
    *,
    db: Session = Depends(deps.get_db),
    borrow_in: BorrowCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin issues books
) -> Any:
    try:
        return crud_library.create_borrow_record(db, borrow=borrow_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/return/{borrow_id}", response_model=BorrowRecord)
def return_book_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    borrow_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin returns books
) -> Any:
    record = crud_library.return_book(db, borrow_id=borrow_id)
    if not record:
        raise HTTPException(status_code=400, detail="Record not found or already returned")
    return record

@router.get("/my-books", response_model=List[BorrowRecord])
def read_my_books(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    # We can infer user_id from current_user.id
    # Note: depends on how `get_current_active_user` returns the user object and if it has ID
    # Usually `current_user` is the ORM object.
    return crud_library.get_my_books(db, user_id=current_user.id)
