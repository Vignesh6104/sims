from sqlalchemy.orm import Session
from app.models.library import Book, BorrowRecord
from app.schemas.library import BookCreate, BorrowCreate
from datetime import date

# Book Operations
def get_book(db: Session, book_id: str):
    return db.query(Book).filter(Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(Book)
    if search:
        query = query.filter(Book.title.ilike(f"%{search}%") | Book.author.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def create_book(db: Session, book: BookCreate):
    db_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        quantity=book.quantity,
        available_quantity=book.quantity # Initially available = total
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# Borrow Operations
def create_borrow_record(db: Session, borrow: BorrowCreate):
    # Check availability
    book = get_book(db, borrow.book_id)
    if not book or book.available_quantity < 1:
        raise ValueError("Book not available")
    
    # Decrement available quantity
    book.available_quantity -= 1
    
    db_borrow = BorrowRecord(
        book_id=borrow.book_id,
        student_id=borrow.student_id,
        teacher_id=borrow.teacher_id,
        due_date=borrow.due_date,
        issue_date=date.today(),
        status="issued"
    )
    db.add(db_borrow)
    db.add(book) # Update book
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def return_book(db: Session, borrow_id: str):
    record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
    if not record or record.status == "returned":
        return None
    
    # Calculate fine (simple logic: 5 units per day late)
    today = date.today()
    record.return_date = today
    record.status = "returned"
    
    if today > record.due_date:
        overdue_days = (today - record.due_date).days
        record.fine_amount = overdue_days * 5.0
    
    # Increment available quantity
    book = get_book(db, record.book_id)
    book.available_quantity += 1
    
    db.add(record)
    db.add(book)
    db.commit()
    db.refresh(record)
    return record

def get_my_books(db: Session, user_id: str):
    return db.query(BorrowRecord).filter(
        (BorrowRecord.student_id == user_id) | (BorrowRecord.teacher_id == user_id)
    ).all()

def get_all_borrowed_books(db: Session):
    return db.query(BorrowRecord).filter(BorrowRecord.status == "issued").all()
