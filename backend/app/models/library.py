"""Library book and borrowing models for the School Information Management System.

This module defines the Book and BorrowRecord models for managing the school
library's book inventory and tracking book borrowing by students and teachers.
"""
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Date, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class Book(Base):
    """Represents a book in the school library catalog.
    
    Book records manage:
    - Library inventory tracking
    - Book availability for borrowing
    - Multiple copies of the same book
    - Book search and cataloging
    
    Relationships:
        borrow_records: One-to-many relationship with BorrowRecord (tracks all borrowing history).
    
    Attributes:
        id (str): Unique identifier (UUID) for the book.
        title (str): Title of the book (indexed for search).
        author (str): Author name(s).
        isbn (str): International Standard Book Number (unique identifier, indexed).
        quantity (int): Total number of copies owned by the library.
        available_quantity (int): Number of copies currently available for borrowing.
    """
    __tablename__ = "books"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)  # Indexed for quick search
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True, nullable=True)  # Unique book identifier
    quantity = Column(Integer, default=1)  # Total copies in library
    available_quantity = Column(Integer, default=1)  # Copies currently available for borrowing
    
    # Relationship: Track all borrowing records for this book
    borrow_records = relationship("BorrowRecord", back_populates="book")

class BorrowRecord(Base):
    """Represents a book borrowing record for a student or teacher.
    
    Borrow records track:
    - Who borrowed which book
    - Issue and due dates
    - Return status
    - Late fees for overdue books
    
    Business rules:
    - Either student_id OR teacher_id must be set (not both)
    - status is "issued" when book is borrowed, "returned" when returned
    - fine_amount is calculated based on days overdue
    
    Relationships:
        book: Many-to-one relationship with Book (record is for a specific book).
        student: Many-to-one relationship with Student (optional - borrower if student).
        teacher: Many-to-one relationship with Teacher (optional - borrower if teacher).
    
    Attributes:
        id (str): Unique identifier (UUID) for the borrow record.
        book_id (str): Foreign key linking to the borrowed book.
        student_id (str): Foreign key linking to student borrower (null if teacher borrowed).
        teacher_id (str): Foreign key linking to teacher borrower (null if student borrowed).
        issue_date (date): Date when the book was issued.
        due_date (date): Date by which the book should be returned.
        return_date (date): Actual return date (null if not yet returned).
        fine_amount (float): Fine charged for late return.
        status (str): Borrowing status - "issued" or "returned".
    """
    __tablename__ = "borrow_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String, ForeignKey("books.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=True)  # Borrower if student
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=True)  # Borrower if teacher
    
    issue_date = Column(Date, default=func.now())  # When book was borrowed
    due_date = Column(Date, nullable=False)  # Return deadline
    return_date = Column(Date, nullable=True)  # Actual return date (null if not returned)
    fine_amount = Column(Float, default=0.0)  # Late return fine
    status = Column(String, default="issued")  # "issued" or "returned"

    # Relationships for accessing borrower and book information
    book = relationship("Book", back_populates="borrow_records")
    student = relationship("Student")
    teacher = relationship("Teacher")
