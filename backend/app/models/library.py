import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Date, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True, nullable=True)
    quantity = Column(Integer, default=1)
    available_quantity = Column(Integer, default=1)
    
    borrow_records = relationship("BorrowRecord", back_populates="book")

class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String, ForeignKey("books.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=True)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=True)
    
    issue_date = Column(Date, default=func.now())
    due_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    fine_amount = Column(Float, default=0.0)
    status = Column(String, default="issued") # issued, returned

    book = relationship("Book", back_populates="borrow_records")
    student = relationship("Student")
    teacher = relationship("Teacher")
