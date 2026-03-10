"""Student Account Management API Endpoints.

This module provides RESTful API endpoints for managing student accounts in the
School Information Management System (SIMS). It handles complete CRUD operations
for student records, bulk CSV uploads, and class-based filtering.

Purpose:
    Centralized student account management for administrators and staff members.
    Provides endpoints for creating, reading, updating, and deleting student records,
    as well as bulk operations through CSV file uploads.

Features:
    - Single student creation (manual entry)
    - Bulk student creation via CSV upload
    - Student record retrieval with pagination
    - Class-based filtering for student queries
    - Student record updates
    - Student record deletion
    - Email uniqueness validation
    - Active status management

Access Control Levels:
    - **Superuser/Admin Only**:
        - POST /upload: Bulk CSV upload of students
        - POST /: Create individual student
        - PUT /{student_id}: Update student information
        - DELETE /{student_id}: Delete student record
    
    - **Staff (Teachers/Admins)**:
        - GET /: List all students with optional filtering
    
    - **Any Authenticated User**:
        - GET /{student_id}: Retrieve specific student details

Student-Specific Features:
    - Roll number assignment and tracking
    - Date of birth management
    - Address information storage
    - Class association (class_id foreign key)
    - Active/inactive status flag
    - Email-based authentication
    - Password hashing (handled in CRUD layer)

CSV Upload Format:
    The bulk upload endpoint expects CSV files with the following headers:
    - email (required): Student's email address
    - password (required): Initial password for the account
    - full_name (optional): Student's full name
    - roll_number (optional): Unique roll number identifier
    - date_of_birth (optional): Date in YYYY-MM-DD format
    - address (optional): Physical address
    - class_id (optional): Associated class identifier
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io
from app.api import deps
from app.crud import crud_student
from app.schemas.student import Student, StudentCreate, StudentUpdate

router = APIRouter()

@router.post("/upload", response_model=dict)
def upload_students(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """Bulk create student accounts via CSV file upload.
    
    This endpoint allows administrators to create multiple student accounts at once
    by uploading a CSV file. Each row in the CSV represents one student record.
    The endpoint validates file format, checks for duplicate emails, and provides
    detailed feedback on success and failure for each row.
    
    Args:
        file (UploadFile): CSV file containing student data. Must have .csv extension.
            Required headers: email, password
            Optional headers: full_name, roll_number, date_of_birth, address, class_id
        db (Session): Database session dependency, automatically injected.
        current_user (Any): Current authenticated superuser, automatically injected.
    
    Authentication:
        Requires superuser/administrator privileges. Only users with admin role can
        perform bulk student uploads.
    
    Returns:
        dict: Upload result summary containing:
            - message (str): Summary message of the operation
            - success_count (int): Number of students successfully created
            - errors (List[str]): List of error messages for failed rows, each
              prefixed with row number for easy identification
    
    Raises:
        HTTPException: 
            - 400: Invalid file format (not a .csv file)
            - 400: Duplicate email found in existing records (per-row basis)
            - 401: Unauthorized - user not authenticated
            - 403: Forbidden - user is not a superuser
            - 422: Validation error in CSV data format
    
    HTTP Status Codes:
        - 200: Successfully processed CSV (check response for per-row details)
        - 400: Bad request (invalid file format or validation errors)
        - 401: Unauthorized (not authenticated)
        - 403: Forbidden (not a superuser)
        - 422: Unprocessable entity (invalid data format)
    
    Notes:
        - The endpoint continues processing even if some rows fail
        - Empty optional fields are handled gracefully
        - Passwords are hashed automatically in the CRUD layer
        - All successfully created students are set to active status
        - Transaction is committed per student, not per batch
    
    Example CSV Format:
        ```
        email,password,full_name,roll_number,date_of_birth,address,class_id
        john@school.com,pass123,John Doe,2024001,2010-05-15,123 Main St,class-101
        jane@school.com,pass456,Jane Smith,2024002,2010-08-20,456 Elm St,class-102
        ```
    """
    # Validate file format before processing
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    # Read and decode the uploaded CSV file content
    content = file.file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(content))
    
    success_count = 0
    errors = []
    
    # Process each row in the CSV file
    for row_num, row in enumerate(csv_reader, start=1):
        try:
            # Validate email uniqueness before attempting to create student
            # This prevents duplicate student records in the database
            if crud_student.get_student_by_email(db, email=row['email']):
                errors.append(f"Row {row_num}: Email {row['email']} already exists.")
                continue

            # Construct StudentCreate schema from CSV row data
            # Handle optional fields with .get() to avoid KeyError
            # Convert empty strings to None for optional date/ID fields
            student_in = StudentCreate(
                email=row['email'],
                password=row['password'],
                full_name=row.get('full_name'),
                roll_number=row.get('roll_number'),
                date_of_birth=row.get('date_of_birth') if row.get('date_of_birth') else None,
                address=row.get('address'),
                class_id=row.get('class_id') if row.get('class_id') else None,
                is_active=True  # All CSV uploads default to active status
            )
            crud_student.create_student(db, student=student_in)
            success_count += 1
        except Exception as e:
            # Capture any validation or database errors for this row
            # Continue processing remaining rows even if one fails
            errors.append(f"Row {row_num}: {str(e)}")

    return {
        "message": f"Processed {success_count} students successfully.",
        "success_count": success_count,
        "errors": errors
    }

@router.get("/", response_model=List[Student])
def read_students(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[str] = Query(None, description="Filter by Class ID"),
    current_user: Any = Depends(deps.get_current_active_staff), # Teachers/Admins
) -> Any:
    """Retrieve a list of student records with optional filtering and pagination.
    
    This endpoint returns student records accessible to staff members (teachers
    and administrators). Results can be filtered by class and paginated using
    skip/limit parameters for efficient data retrieval.
    
    Query Parameters:
        skip (int, optional): Number of records to skip for pagination. 
            Defaults to 0. Must be >= 0.
        limit (int, optional): Maximum number of records to return. 
            Defaults to 100. Must be > 0.
        class_id (str, optional): Filter students by their assigned class.
            When provided, only returns students belonging to the specified class.
            When omitted, returns all students in the system.
    
    Args:
        db (Session): Database session dependency, automatically injected.
        skip (int): Pagination offset.
        limit (int): Maximum results to return.
        class_id (Optional[str]): Class ID filter.
        current_user (Any): Current authenticated staff user, automatically injected.
    
    Authentication:
        Requires staff privileges (teacher or administrator role). Regular students
        cannot access the full student list.
    
    Returns:
        List[Student]: List of student records matching the filter criteria.
            Each student object includes all fields defined in the Student schema
            (id, email, full_name, roll_number, date_of_birth, address, class_id, 
            is_active, created_at, updated_at).
    
    Raises:
        HTTPException:
            - 401: Unauthorized - user not authenticated
            - 403: Forbidden - user is not staff (not teacher or admin)
            - 422: Validation error in query parameters
    
    HTTP Status Codes:
        - 200: Successfully retrieved student list
        - 401: Unauthorized (not authenticated)
        - 403: Forbidden (not staff member)
        - 422: Unprocessable entity (invalid query parameters)
    
    Notes:
        - Empty list is returned if no students match the criteria
        - Results are ordered by creation date (newest first) in the CRUD layer
        - For large datasets, use pagination to avoid performance issues
    """
    # Apply class-based filtering if class_id is provided, otherwise return all students
    if class_id:
        return crud_student.get_students_by_class(db, class_id=class_id, skip=skip, limit=limit)
    return crud_student.get_students(db, skip=skip, limit=limit)

@router.post("/", response_model=Student)
def create_student(
    *,
    db: Session = Depends(deps.get_db),
    student_in: StudentCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin can manually create/force-add
) -> Any:
    """Create a new student account manually.
    
    This endpoint allows administrators to create individual student accounts
    one at a time. It performs email uniqueness validation before creating
    the record to prevent duplicate accounts.
    
    Request Body:
        student_in (StudentCreate): Student creation data containing:
            - email (str, required): Unique email address for the student
            - password (str, required): Initial password (will be hashed)
            - full_name (str, optional): Student's full name
            - roll_number (str, optional): Unique roll number identifier
            - date_of_birth (str, optional): Birth date in YYYY-MM-DD format
            - address (str, optional): Physical address
            - class_id (str, optional): ID of the class to assign student to
            - is_active (bool, optional): Account active status, defaults to True
    
    Args:
        db (Session): Database session dependency, automatically injected.
        student_in (StudentCreate): Student creation schema with required fields.
        current_user (Any): Current authenticated superuser, automatically injected.
    
    Authentication:
        Requires superuser/administrator privileges. Only admins can manually
        create individual student accounts.
    
    Returns:
        Student: The newly created student record including:
            - Auto-generated student ID
            - All provided fields
            - Timestamps (created_at, updated_at)
            - Hashed password (not returned in response)
    
    Raises:
        HTTPException:
            - 400: Bad request - student with this email already exists
            - 401: Unauthorized - user not authenticated
            - 403: Forbidden - user is not a superuser
            - 422: Validation error in request body data
    
    HTTP Status Codes:
        - 200: Student successfully created
        - 400: Bad request (duplicate email)
        - 401: Unauthorized (not authenticated)
        - 403: Forbidden (not a superuser)
        - 422: Unprocessable entity (validation error)
    
    Notes:
        - Email must be unique across all students
        - Password is automatically hashed before storage
        - Roll number should be unique but is not enforced at API level
        - For bulk creation, use the /upload endpoint instead
    """
    # Check if a student with this email already exists in the database
    student = crud_student.get_student_by_email(db, email=student_in.email)
    if student:
        raise HTTPException(status_code=400, detail="Student already exists")
    return crud_student.create_student(db, student=student_in)

@router.get("/{student_id}", response_model=Student)
def read_student(
    student_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve detailed information for a specific student.
    
    This endpoint returns complete details for a single student identified by
    their unique student ID. Any authenticated user can access student details.
    
    Path Parameters:
        student_id (str): Unique identifier of the student to retrieve.
            This is the auto-generated ID assigned when the student was created.
    
    Args:
        student_id (str): The unique student identifier.
        db (Session): Database session dependency, automatically injected.
        current_user (Any): Current authenticated user, automatically injected.
    
    Authentication:
        Requires authentication. Any active user (student, teacher, or admin)
        can view student details.
    
    Returns:
        Student: Complete student record including:
            - id (str): Unique student identifier
            - email (str): Student's email address
            - full_name (str): Student's full name
            - roll_number (str): Student's roll number
            - date_of_birth (str): Date of birth
            - address (str): Physical address
            - class_id (str): Associated class ID
            - is_active (bool): Account active status
            - created_at (datetime): Record creation timestamp
            - updated_at (datetime): Last update timestamp
    
    Raises:
        HTTPException:
            - 404: Not found - student with specified ID does not exist
            - 401: Unauthorized - user not authenticated
            - 422: Validation error in student_id format
    
    HTTP Status Codes:
        - 200: Student found and returned successfully
        - 401: Unauthorized (not authenticated)
        - 404: Not found (student does not exist)
        - 422: Unprocessable entity (invalid student_id format)
    
    Notes:
        - This endpoint does not return the student's password hash
        - Inactive students can still be retrieved
    """
    student = crud_student.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=Student)
def update_student(
    *,
    db: Session = Depends(deps.get_db),
    student_id: str,
    student_in: StudentUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """Update an existing student's information.
    
    This endpoint allows administrators to modify student account details.
    Only fields provided in the request body will be updated; omitted fields
    remain unchanged (partial update support).
    
    Path Parameters:
        student_id (str): Unique identifier of the student to update.
    
    Request Body:
        student_in (StudentUpdate): Student update data, all fields optional:
            - email (str, optional): New email address
            - password (str, optional): New password (will be hashed)
            - full_name (str, optional): Updated full name
            - roll_number (str, optional): Updated roll number
            - date_of_birth (str, optional): Updated birth date (YYYY-MM-DD)
            - address (str, optional): Updated address
            - class_id (str, optional): New class assignment
            - is_active (bool, optional): Updated active status
    
    Args:
        db (Session): Database session dependency, automatically injected.
        student_id (str): The student's unique identifier.
        student_in (StudentUpdate): Partial or complete update data.
        current_user (Any): Current authenticated superuser, automatically injected.
    
    Authentication:
        Requires superuser/administrator privileges. Only admins can update
        student information.
    
    Returns:
        Student: The updated student record with all current field values,
            including the updated timestamp.
    
    Raises:
        HTTPException:
            - 404: Not found - student with specified ID does not exist
            - 401: Unauthorized - user not authenticated
            - 403: Forbidden - user is not a superuser
            - 422: Validation error in request data
    
    HTTP Status Codes:
        - 200: Student updated successfully
        - 401: Unauthorized (not authenticated)
        - 403: Forbidden (not a superuser)
        - 404: Not found (student does not exist)
        - 422: Unprocessable entity (validation error)
    
    Notes:
        - Only provided fields are updated (PATCH-like behavior)
        - Email updates should maintain uniqueness (not validated here)
        - Password updates trigger automatic hashing
        - The updated_at timestamp is automatically updated
    """
    # Verify student exists before attempting update
    student = crud_student.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # Perform partial update with only the fields provided in student_in
    student = crud_student.update_student(db, db_student=student, student_update=student_in)
    return student

@router.delete("/{student_id}", response_model=Student)
def delete_student(
    *,
    db: Session = Depends(deps.get_db),
    student_id: str,
    current_user: Any = Depends(deps.get_current_active_superuser), # Only Admin
) -> Any:
    """Delete a student account from the system.
    
    This endpoint permanently removes a student record from the database.
    The operation is irreversible and should be used with caution. Consider
    deactivating the student (is_active=False) instead of deletion for
    maintaining historical records.
    
    Path Parameters:
        student_id (str): Unique identifier of the student to delete.
    
    Args:
        db (Session): Database session dependency, automatically injected.
        student_id (str): The student's unique identifier.
        current_user (Any): Current authenticated superuser, automatically injected.
    
    Authentication:
        Requires superuser/administrator privileges. Only admins can delete
        student accounts.
    
    Returns:
        Student: The deleted student record as it existed before deletion.
            This provides confirmation of which record was removed.
    
    Raises:
        HTTPException:
            - 404: Not found - student with specified ID does not exist
            - 401: Unauthorized - user not authenticated
            - 403: Forbidden - user is not a superuser
            - 422: Validation error in student_id format
    
    HTTP Status Codes:
        - 200: Student deleted successfully
        - 401: Unauthorized (not authenticated)
        - 403: Forbidden (not a superuser)
        - 404: Not found (student does not exist)
        - 422: Unprocessable entity (invalid student_id)
    
    Notes:
        - This is a hard delete, not a soft delete
        - Associated records (enrollments, grades) may be affected
        - Consider using update with is_active=False for soft deletion
        - The operation cannot be undone
        - Database foreign key constraints may prevent deletion
    """
    # Verify student exists before attempting deletion
    student = crud_student.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # Perform hard delete from database
    return crud_student.delete_student(db, student_id=student_id)