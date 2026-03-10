"""
Library Book Management and Borrowing System API.

This module provides RESTful API endpoints for managing a library's book catalog
and borrowing system. It enables book management, issue/return operations, search
functionality, and borrow tracking.

Features:
    - Book Catalog Management: Create and browse books in the library
    - Book Search: Search books by title, author, or other attributes
    - Issue Books: Create borrow records when books are issued to users
    - Return Books: Process book returns and update borrow records
    - Borrow Tracking: Track current and historical borrows per user

Access Control:
    - Admin users (superuser): Can manage books, issue books, and process returns
    - All authenticated users: Can view books, search catalog, and view their borrow history
    - Unauthenticated users: No access to any endpoints
"""
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
    """
    Retrieve books from the library catalog.
    
    This endpoint returns a paginated list of books from the library. Users can
    optionally search for books using keywords that match against book attributes
    like title, author, ISBN, etc.
    
    Parameters:
        db (Session): Database session dependency
        skip (int): Number of records to skip for pagination (default: 0)
        limit (int): Maximum number of records to return (default: 100)
        search (Optional[str]): Search query string to filter books (default: None)
        current_user (Any): Currently authenticated user (injected by auth dependency)
    
    Authentication:
        Required: Active user account
        Role: Any authenticated user
    
    Returns:
        List[Book]: List of book objects matching the search criteria
    
    HTTP Status Codes:
        200: Books retrieved successfully
        401: User not authenticated
        422: Invalid query parameters
    
    Example:
        GET /books?skip=0&limit=10&search=python
    """
    return crud_library.get_books(db, skip=skip, limit=limit, search=search)

@router.post("/books", response_model=Book)
def create_book(
    *,
    db: Session = Depends(deps.get_db),
    book_in: BookCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin only
) -> Any:
    """
    Add a new book to the library catalog.
    
    This endpoint allows administrators to create new book records in the library
    catalog. The book data includes title, author, ISBN, total copies, and other
    metadata required for catalog management.
    
    Parameters:
        db (Session): Database session dependency
        book_in (BookCreate): Book creation schema with required book details
        current_user (Any): Currently authenticated superuser (injected by auth dependency)
    
    Authentication:
        Required: Active superuser (admin) account
        Role: Admin only
    
    Returns:
        Book: The newly created book object with assigned ID and timestamps
    
    Raises:
        HTTPException: 403 if user is not an admin
        HTTPException: 422 if book data validation fails
    
    HTTP Status Codes:
        200: Book created successfully
        401: User not authenticated
        403: User is not an admin
        422: Invalid book data provided
    
    Example:
        POST /books
        Body: {"title": "Python Basics", "author": "John Doe", "isbn": "1234567890", "total_copies": 5}
    """
    return crud_library.create_book(db, book=book_in)

@router.post("/issue", response_model=BorrowRecord)
def issue_book(
    *,
    db: Session = Depends(deps.get_db),
    borrow_in: BorrowCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin issues books
) -> Any:
    """
    Issue a book to a user (create borrow record).
    
    This endpoint allows administrators to issue books to users by creating a new
    borrow record. It validates book availability before creating the record and
    decrements the available copies count.
    
    Parameters:
        db (Session): Database session dependency
        borrow_in (BorrowCreate): Borrow creation schema with book_id and user_id
        current_user (Any): Currently authenticated superuser (injected by auth dependency)
    
    Authentication:
        Required: Active superuser (admin) account
        Role: Admin only
    
    Returns:
        BorrowRecord: The newly created borrow record with issue date and status
    
    Raises:
        HTTPException: 400 if book is not available or validation fails
        HTTPException: 403 if user is not an admin
        HTTPException: 422 if borrow data is invalid
    
    HTTP Status Codes:
        200: Book issued successfully
        400: Book not available or validation error
        401: User not authenticated
        403: User is not an admin
        422: Invalid borrow data provided
    
    Example:
        POST /issue
        Body: {"book_id": "uuid-here", "user_id": "uuid-here"}
    """
    try:
        # Check book availability and create borrow record
        # The CRUD layer validates that available_copies > 0 before issuing
        return crud_library.create_borrow_record(db, borrow=borrow_in)
    except ValueError as e:
        # Handle cases where book is unavailable or doesn't exist
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/return/{borrow_id}", response_model=BorrowRecord)
def return_book_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    borrow_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin returns books
) -> Any:
    """
    Process a book return.
    
    This endpoint allows administrators to process book returns by updating the
    borrow record with a return date and incrementing the book's available copies.
    
    Parameters:
        db (Session): Database session dependency
        borrow_id (str): UUID of the borrow record to process
        current_user (Any): Currently authenticated superuser (injected by auth dependency)
    
    Authentication:
        Required: Active superuser (admin) account
        Role: Admin only
    
    Returns:
        BorrowRecord: The updated borrow record with return date set
    
    Raises:
        HTTPException: 400 if borrow record not found or already returned
        HTTPException: 403 if user is not an admin
    
    HTTP Status Codes:
        200: Book returned successfully
        400: Borrow record not found or already returned
        401: User not authenticated
        403: User is not an admin
    
    Example:
        POST /return/uuid-of-borrow-record
    """
    # Process the return and update borrow record with return date
    # The CRUD layer increments available_copies when marking as returned
    record = crud_library.return_book(db, borrow_id=borrow_id)
    if not record:
        # Borrow record either doesn't exist or is already marked as returned
        raise HTTPException(status_code=400, detail="Record not found or already returned")
    return record

@router.get("/my-books", response_model=List[BorrowRecord])
def read_my_books(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve current user's borrow history.
    
    This endpoint returns all borrow records for the currently authenticated user,
    including both active borrows (not yet returned) and historical borrows
    (already returned). Users can track which books they have borrowed and their
    return status.
    
    Parameters:
        db (Session): Database session dependency
        current_user (Any): Currently authenticated user (injected by auth dependency)
    
    Authentication:
        Required: Active user account
        Role: Any authenticated user
    
    Returns:
        List[BorrowRecord]: List of all borrow records for the current user
    
    HTTP Status Codes:
        200: Borrow records retrieved successfully
        401: User not authenticated
    
    Example:
        GET /my-books
    """
    # Extract user_id from the authenticated user object
    # The auth dependency returns the full ORM user object with an id attribute
    return crud_library.get_my_books(db, user_id=current_user.id)
