"""CRUD operations for library book and borrowing management.

This module handles book catalog management, borrowing transactions,
return processing with fine calculation, and availability tracking.
Includes business logic for inventory management.
"""

from sqlalchemy.orm import Session
from app.models.library import Book, BorrowRecord
from app.schemas.library import BookCreate, BorrowCreate
from datetime import date


# Book Operations
def get_book(db: Session, book_id: str):
    """Retrieve a book by its unique identifier.
    
    Args:
        db: Database session for query execution.
        book_id: Unique identifier of the book.
        
    Returns:
        Book object if found, None otherwise.
    """
    return db.query(Book).filter(Book.id == book_id).first()


def get_books(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    """Retrieve books with optional search filtering.
    
    Supports case-insensitive search across title and author fields.
    
    Args:
        db: Database session for query execution.
        skip: Number of records to skip for pagination (default: 0).
        limit: Maximum number of records to return (default: 100).
        search: Optional search term for title/author (default: None).
        
    Returns:
        List of Book objects matching search criteria.
        
    Note:
        Uses SQL ILIKE for case-insensitive pattern matching on title OR author.
    """
    query = db.query(Book)
    if search:
        # Case-insensitive search on title or author
        query = query.filter(Book.title.ilike(f"%{search}%") | Book.author.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


def create_book(db: Session, book: BookCreate):
    """Add a new book to the library catalog.
    
    Args:
        db: Database session for query execution.
        book: BookCreate schema with book details.
        
    Returns:
        Newly created Book object with generated ID.
        
    Note:
        Initially sets available_quantity equal to total quantity.
    """
    db_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        quantity=book.quantity,
        available_quantity=book.quantity  # Initially all copies are available
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


# Borrow Operations
def create_borrow_record(db: Session, borrow: BorrowCreate):
    """Issue a book to a student or teacher.
    
    Checks book availability and decrements the available quantity.
    
    Args:
        db: Database session for query execution.
        borrow: BorrowCreate schema with borrow details.
        
    Returns:
        Newly created BorrowRecord object with generated ID.
        
    Raises:
        ValueError: If book is not found or not available.
        
    Note:
        Business logic: Decrements available_quantity when book is issued.
        Sets status to "issued" and issue_date to today.
    """
    # Check availability before issuing
    book = get_book(db, borrow.book_id)
    if not book or book.available_quantity < 1:
        raise ValueError("Book not available")
    
    # Decrement available quantity (inventory management)
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
    db.add(book)  # Update book inventory
    db.commit()
    db.refresh(db_borrow)
    return db_borrow


def return_book(db: Session, borrow_id: str):
    """Process book return with automatic fine calculation.
    
    Updates borrow record status, increments available quantity,
    and calculates fines for overdue returns.
    
    Args:
        db: Database session for query execution.
        borrow_id: Unique identifier of the borrow record.
        
    Returns:
        Updated BorrowRecord object with return date and fine, or None if not found.
        
    Note:
        Fine calculation logic: 5 currency units per day overdue.
        Only calculates fine if return_date > due_date.
        Increments book's available_quantity when returned.
    """
    record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
    if not record or record.status == "returned":
        return None
    
    # Calculate fine for overdue books
    today = date.today()
    record.return_date = today
    record.status = "returned"
    
    # Fine calculation: 5 units per day late
    if today > record.due_date:
        overdue_days = (today - record.due_date).days
        record.fine_amount = overdue_days * 5.0
    
    # Increment available quantity (return to inventory)
    book = get_book(db, record.book_id)
    book.available_quantity += 1
    
    db.add(record)
    db.add(book)
    db.commit()
    db.refresh(record)
    return record


def get_my_books(db: Session, user_id: str):
    """Retrieve all borrow records for a specific user (student or teacher).
    
    Args:
        db: Database session for query execution.
        user_id: Unique identifier of the user (student or teacher).
        
    Returns:
        List of BorrowRecord objects for the specified user.
        
    Note:
        Uses OR condition to check both student_id and teacher_id.
    """
    return db.query(BorrowRecord).filter(
        (BorrowRecord.student_id == user_id) | (BorrowRecord.teacher_id == user_id)
    ).all()


def get_all_borrowed_books(db: Session):
    """Retrieve all currently borrowed (not returned) books.
    
    Args:
        db: Database session for query execution.
        
    Returns:
        List of BorrowRecord objects with status "issued".
    """
    return db.query(BorrowRecord).filter(BorrowRecord.status == "issued").all()
