"""
Timetable Management API

This module provides endpoints for managing class and teacher timetables in the 
School Information Management System (SIMS).

Purpose:
    - Manage timetable entries for classes and teachers
    - Enable viewing timetables by class or teacher
    - Support creation and deletion of timetable entries

Features:
    - View timetable by class ID
    - View timetable by teacher ID
    - Create new timetable entries
    - Delete existing timetable entries

Access Control:
    - Viewing timetables: Available to all authenticated users
    - Creating entries: Restricted to administrators/superusers only
    - Deleting entries: Restricted to administrators/superusers only
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_timetable
from app.schemas.timetable import Timetable, TimetableCreate

router = APIRouter()

@router.get("/class/{class_id}", response_model=List[Timetable])
def read_class_timetable(
    class_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve timetable entries for a specific class.
    
    Fetches all timetable entries associated with the given class ID, including 
    information about subjects, teachers, time slots, and days.
    
    Parameters:
        class_id (str): The unique identifier of the class
        db (Session): Database session dependency
        current_user (Any): Current authenticated user dependency
    
    Authentication:
        Requires: Active user authentication
        Access Level: All authenticated users
    
    Returns:
        List[Timetable]: List of timetable entries for the specified class.
                         Returns empty list if no entries found.
    
    Raises:
        HTTPException: 
            - 401 Unauthorized: If user is not authenticated
            - 403 Forbidden: If user account is inactive
    
    HTTP Status Codes:
        200 OK: Successfully retrieved timetable entries
        401 Unauthorized: Authentication required
        403 Forbidden: User account is inactive
    """
    return crud_timetable.get_timetable_by_class(db, class_id=class_id)

@router.get("/teacher/{teacher_id}", response_model=List[Timetable])
def read_teacher_timetable(
    teacher_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve timetable entries for a specific teacher.
    
    Fetches all timetable entries where the given teacher is assigned, including 
    information about classes, subjects, time slots, and days.
    
    Parameters:
        teacher_id (str): The unique identifier of the teacher
        db (Session): Database session dependency
        current_user (Any): Current authenticated user dependency
    
    Authentication:
        Requires: Active user authentication
        Access Level: All authenticated users
    
    Returns:
        List[Timetable]: List of timetable entries for the specified teacher.
                         Returns empty list if no entries found.
    
    Raises:
        HTTPException:
            - 401 Unauthorized: If user is not authenticated
            - 403 Forbidden: If user account is inactive
    
    HTTP Status Codes:
        200 OK: Successfully retrieved timetable entries
        401 Unauthorized: Authentication required
        403 Forbidden: User account is inactive
    """
    return crud_timetable.get_timetable_by_teacher(db, teacher_id=teacher_id)

@router.post("/", response_model=Timetable)
def create_timetable_entry(
    *,
    db: Session = Depends(deps.get_db),
    timetable_in: TimetableCreate,
    current_user: Any = Depends(deps.get_current_active_superuser), # Admin only
) -> Any:
    """
    Create a new timetable entry.
    
    Creates a new timetable entry with the specified class, teacher, subject, 
    day, and time slot information. Only administrators can create timetable entries.
    
    Parameters:
        db (Session): Database session dependency
        timetable_in (TimetableCreate): Timetable entry data including:
            - class_id: ID of the class
            - teacher_id: ID of the assigned teacher
            - subject_id: ID of the subject
            - day: Day of the week
            - time_slot: Time slot for the class
        current_user (Any): Current authenticated superuser dependency
    
    Authentication:
        Requires: Active superuser/administrator authentication
        Access Level: Administrators only
    
    Returns:
        Timetable: The newly created timetable entry with all fields populated,
                   including the generated entry ID.
    
    Raises:
        HTTPException:
            - 400 Bad Request: If timetable data is invalid or conflicts with existing entries
            - 401 Unauthorized: If user is not authenticated
            - 403 Forbidden: If user is not a superuser/administrator
            - 404 Not Found: If referenced class, teacher, or subject doesn't exist
    
    HTTP Status Codes:
        200 OK: Timetable entry created successfully
        400 Bad Request: Invalid input data or scheduling conflict
        401 Unauthorized: Authentication required
        403 Forbidden: Insufficient permissions (admin required)
        404 Not Found: Referenced entity not found
    """
    return crud_timetable.create_timetable_entry(db, timetable_in=timetable_in)

@router.delete("/{entry_id}", response_model=Timetable)
def delete_timetable_entry(
    entry_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a timetable entry.
    
    Removes a timetable entry from the system by its unique identifier. 
    Only administrators can delete timetable entries.
    
    Parameters:
        entry_id (str): The unique identifier of the timetable entry to delete
        db (Session): Database session dependency
        current_user (Any): Current authenticated superuser dependency
    
    Authentication:
        Requires: Active superuser/administrator authentication
        Access Level: Administrators only
    
    Returns:
        Timetable: The deleted timetable entry data for confirmation.
    
    Raises:
        HTTPException:
            - 401 Unauthorized: If user is not authenticated
            - 403 Forbidden: If user is not a superuser/administrator
            - 404 Not Found: If timetable entry with given ID doesn't exist
    
    HTTP Status Codes:
        200 OK: Timetable entry deleted successfully
        401 Unauthorized: Authentication required
        403 Forbidden: Insufficient permissions (admin required)
        404 Not Found: Timetable entry not found
    """
    return crud_timetable.delete_timetable_entry(db, entry_id=entry_id)
