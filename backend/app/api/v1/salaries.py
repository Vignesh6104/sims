"""
Salary and Payroll Management API.

This module provides endpoints for managing salary and payroll operations within
the School Information Management System (SIMS).

Purpose:
    Handle salary and payroll-related data access and management for school staff.

Features:
    - View all salary records for staff members
    - View payroll records and payment history
    - Manage compensation and payment tracking

Access Control:
    All endpoints in this module require administrator (superuser) privileges.
    Only authenticated users with admin rights can access salary and payroll data.
"""
from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.salary import Salary, PayrollRecord

router = APIRouter()

@router.get("/salaries")
def read_salaries(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
):
    """
    Retrieve all salary records.

    This endpoint returns a list of all salary records for staff members in the system.
    Provides access to compensation information including base salary, allowances,
    and other payment details.

    Parameters:
        db (Session): Database session dependency for executing queries.
        current_user (Any): Currently authenticated superuser. Must have admin privileges.

    Authentication:
        Requires valid JWT token with superuser/admin privileges.
        Non-admin users will receive a 403 Forbidden response.

    Returns:
        List[Salary]: A list of all salary records from the database.
            Each record contains salary details for a staff member.

    Raises:
        HTTPException: 401 Unauthorized if authentication token is missing or invalid.
        HTTPException: 403 Forbidden if user lacks superuser privileges.
        HTTPException: 500 Internal Server Error if database query fails.

    HTTP Status Codes:
        200: Successfully retrieved salary records.
        401: Unauthorized - Invalid or missing authentication token.
        403: Forbidden - User lacks required admin privileges.
        500: Internal Server Error - Database or server error occurred.
    """
    return db.query(Salary).all()

@router.get("/payroll")
def read_payroll(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
):
    """
    Retrieve all payroll records.

    This endpoint returns a complete list of payroll records containing payment history
    and transaction details for all staff members. Includes information about salary
    disbursements, payment dates, and related payroll processing data.

    Parameters:
        db (Session): Database session dependency for executing queries.
        current_user (Any): Currently authenticated superuser. Must have admin privileges.

    Authentication:
        Requires valid JWT token with superuser/admin privileges.
        Non-admin users will receive a 403 Forbidden response.

    Returns:
        List[PayrollRecord]: A list of all payroll records from the database.
            Each record contains payment transaction details for staff salary disbursements.

    Raises:
        HTTPException: 401 Unauthorized if authentication token is missing or invalid.
        HTTPException: 403 Forbidden if user lacks superuser privileges.
        HTTPException: 500 Internal Server Error if database query fails.

    HTTP Status Codes:
        200: Successfully retrieved payroll records.
        401: Unauthorized - Invalid or missing authentication token.
        403: Forbidden - User lacks required admin privileges.
        500: Internal Server Error - Database or server error occurred.
    """
    return db.query(PayrollRecord).all()
