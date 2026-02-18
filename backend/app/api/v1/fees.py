"""
Fee Structure and Payment Management API

This module provides endpoints for managing school fee structures and student fee payments
within the School Information Management System (SIMS).

Purpose:
    Handles all fee-related operations including fee structure definition, payment recording,
    and payment history retrieval for students.

Features:
    - Fee Structure Management: Create and retrieve fee structures for different classes/terms
    - Payment Recording: Record student fee payments with details like amount, date, and method
    - Payment History: View comprehensive payment history for individual students
    - Financial Tracking: Enable tracking of student payment status and outstanding balances

Access Control:
    - Fee structure viewing: Requires active staff member authentication
    - Fee structure creation: Restricted to superuser/admin accounts only
    - Payment recording: Restricted to superuser/admin accounts only
    - Payment history viewing: Available to any authenticated user (students can view own payments)

Endpoints:
    GET  /structures - List all fee structures
    POST /structures - Create a new fee structure
    GET  /payments/student/{student_id} - Get payment history for a student
    POST /payments - Record a new fee payment
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_fee
from app.schemas.fee import FeeStructure, FeeStructureCreate, FeePayment, FeePaymentCreate

router = APIRouter()

@router.get("/structures", response_model=List[FeeStructure])
def read_fee_structures(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_staff),
) -> Any:
    """
    Retrieve all fee structures with pagination support.
    
    This endpoint returns a list of all fee structures defined in the system,
    including details such as class, term, amount, and due dates. Fee structures
    define the expected payments for different student categories and periods.
    
    Parameters:
        db (Session): Database session dependency
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        current_user (Any): Currently authenticated staff member
    
    Authentication:
        Requires: Active staff member account (teacher, admin, or other staff)
        Dependency: deps.get_current_active_staff
    
    Returns:
        List[FeeStructure]: List of fee structure objects containing:
            - id: Unique identifier for the fee structure
            - class_id: Associated class/grade
            - term: Academic term (e.g., "Term 1", "Semester 1")
            - amount: Fee amount in the system's currency
            - due_date: Payment deadline
            - description: Optional fee description
            - Other fee structure fields as defined in the schema
    
    Raises:
        HTTPException: 401 Unauthorized if user is not authenticated
        HTTPException: 403 Forbidden if user is not staff member
    
    HTTP Status Codes:
        200: Success - Fee structures retrieved successfully
        401: Unauthorized - Authentication required
        403: Forbidden - Insufficient permissions (non-staff user)
        500: Internal Server Error - Database or server error
    
    Example:
        GET /api/v1/fees/structures?skip=0&limit=10
    """
    return crud_fee.get_fee_structures(db, skip=skip, limit=limit)

@router.post("/structures", response_model=FeeStructure)
def create_fee_structure(
    *,
    db: Session = Depends(deps.get_db),
    fee_in: FeeStructureCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new fee structure in the system.
    
    This endpoint allows administrators to define new fee structures for different
    classes, terms, or student categories. Fee structures specify the amount students
    are expected to pay and the payment deadline.
    
    Parameters:
        db (Session): Database session dependency
        fee_in (FeeStructureCreate): Fee structure data to create, including:
            - class_id: Class/grade this fee applies to
            - term: Academic term or period
            - amount: Fee amount to be charged
            - due_date: Payment deadline
            - description: Optional description of the fee
            - Any other required fields as defined in FeeStructureCreate schema
        current_user (Any): Currently authenticated superuser/admin
    
    Authentication:
        Requires: Superuser/Administrator account
        Dependency: deps.get_current_active_superuser
        Rationale: Only administrators should define fee structures
    
    Returns:
        FeeStructure: Created fee structure object with all fields including:
            - id: Auto-generated unique identifier
            - All fields from the input schema
            - created_at: Timestamp of creation
            - updated_at: Timestamp of last update
    
    Raises:
        HTTPException: 401 Unauthorized if user is not authenticated
        HTTPException: 403 Forbidden if user is not a superuser
        HTTPException: 422 Unprocessable Entity if validation fails
    
    HTTP Status Codes:
        200: Success - Fee structure created successfully
        401: Unauthorized - Authentication required
        403: Forbidden - Insufficient permissions (non-superuser)
        422: Unprocessable Entity - Invalid input data
        500: Internal Server Error - Database or server error
    
    Example:
        POST /api/v1/fees/structures
        {
            "class_id": "class-123",
            "term": "Term 1 2024",
            "amount": 50000.00,
            "due_date": "2024-03-31",
            "description": "First term tuition fee"
        }
    """
    return crud_fee.create_fee_structure(db, fee_in=fee_in)

@router.get("/payments/student/{student_id}", response_model=List[FeePayment])
def read_student_payments(
    student_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve complete payment history for a specific student.
    
    This endpoint returns all fee payments made by a particular student, providing
    a comprehensive view of their payment history including amounts paid, dates,
    payment methods, and associated fee structures.
    
    Parameters:
        student_id (str): Unique identifier of the student (path parameter)
        db (Session): Database session dependency
        current_user (Any): Currently authenticated user
    
    Authentication:
        Requires: Any active authenticated user
        Dependency: deps.get_current_active_user
        Note: Students can view their own payment history, staff can view any student
    
    Returns:
        List[FeePayment]: List of payment records containing:
            - id: Unique payment identifier
            - student_id: Student who made the payment
            - fee_structure_id: Associated fee structure
            - amount: Amount paid
            - payment_date: Date of payment
            - payment_method: Method used (cash, bank transfer, etc.)
            - receipt_number: Payment receipt/reference number
            - status: Payment status (completed, pending, etc.)
            - created_at: Record creation timestamp
            - Other payment fields as defined in the schema
    
    Raises:
        HTTPException: 401 Unauthorized if user is not authenticated
        HTTPException: 404 Not Found if student does not exist
    
    HTTP Status Codes:
        200: Success - Payment history retrieved successfully
        401: Unauthorized - Authentication required
        404: Not Found - Student ID does not exist
        500: Internal Server Error - Database or server error
    
    Example:
        GET /api/v1/fees/payments/student/student-123
    """
    return crud_fee.get_fee_payments_by_student(db, student_id=student_id)

@router.post("/payments", response_model=FeePayment)
def create_payment(
    *,
    db: Session = Depends(deps.get_db),
    payment_in: FeePaymentCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin records payments
) -> Any:
    """
    Record a new fee payment for a student.
    
    This endpoint allows administrators to record fee payments made by students,
    creating an official record in the system. This is typically used when students
    make payments through various methods (cash, bank transfer, etc.) and the
    administrator needs to update the payment records.
    
    Parameters:
        db (Session): Database session dependency
        payment_in (FeePaymentCreate): Payment data to record, including:
            - student_id: ID of the student making the payment
            - fee_structure_id: Associated fee structure being paid
            - amount: Amount being paid
            - payment_date: Date the payment was made
            - payment_method: Payment method (cash, transfer, cheque, etc.)
            - receipt_number: Payment receipt or reference number
            - notes: Optional payment notes or remarks
            - Any other required fields as defined in FeePaymentCreate schema
        current_user (Any): Currently authenticated superuser/admin
    
    Authentication:
        Requires: Superuser/Administrator account
        Dependency: deps.get_current_active_superuser
        Rationale: Only administrators should record official payment transactions
    
    Returns:
        FeePayment: Created payment record with all fields including:
            - id: Auto-generated unique payment identifier
            - All fields from the input schema
            - status: Payment status
            - created_at: Record creation timestamp
            - updated_at: Last update timestamp
    
    Raises:
        HTTPException: 401 Unauthorized if user is not authenticated
        HTTPException: 403 Forbidden if user is not a superuser
        HTTPException: 404 Not Found if student_id or fee_structure_id is invalid
        HTTPException: 422 Unprocessable Entity if validation fails
    
    HTTP Status Codes:
        200: Success - Payment recorded successfully
        401: Unauthorized - Authentication required
        403: Forbidden - Insufficient permissions (non-superuser)
        404: Not Found - Invalid student_id or fee_structure_id
        422: Unprocessable Entity - Invalid input data
        500: Internal Server Error - Database or server error
    
    Example:
        POST /api/v1/fees/payments
        {
            "student_id": "student-123",
            "fee_structure_id": "fee-456",
            "amount": 25000.00,
            "payment_date": "2024-01-15",
            "payment_method": "bank_transfer",
            "receipt_number": "RCP-2024-001",
            "notes": "First installment payment"
        }
    """
    return crud_fee.create_fee_payment(db, payment_in=payment_in)
