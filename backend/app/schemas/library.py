from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# Book Schemas
class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    quantity: int = 1

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class BookInDBBase(BookBase):
    id: str
    available_quantity: int

    class Config:
        from_attributes = True

class Book(BookInDBBase):
    pass

# Borrow Record Schemas
class BorrowBase(BaseModel):
    book_id: str
    due_date: date

class BorrowCreate(BorrowBase):
    student_id: Optional[str] = None
    teacher_id: Optional[str] = None

class BorrowReturn(BaseModel):
    return_date: date = date.today()

class BorrowRecordInDB(BorrowBase):
    id: str
    issue_date: date
    return_date: Optional[date] = None
    fine_amount: float = 0.0
    status: str
    student_id: Optional[str] = None
    teacher_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class BorrowRecord(BorrowRecordInDB):
    book: Optional[Book] = None
