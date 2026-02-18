"""
School Asset and Resource Management API.

This module provides endpoints for managing school assets and resources inventory.

Purpose:
    - Manage and track school assets and resources
    - Provide inventory visibility for school staff
    - Support asset allocation and monitoring

Features:
    - View complete assets inventory
    - Filter and query asset information
    - Staff-level access control

Access Control:
    - All endpoints require authentication
    - Staff-level permissions required (teachers, administrators)
    - Students do not have access to asset management
"""
from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.asset import Asset

router = APIRouter()

@router.get("/")
def read_assets(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_staff),
):
    """
    Retrieve all school assets from inventory.

    This endpoint returns a complete list of all assets and resources
    registered in the school's inventory system. Assets include physical
    items, equipment, facilities, and other resources tracked by the school.

    Parameters:
        db (Session): Database session dependency for querying assets.
            Automatically injected by FastAPI dependency injection.
        current_user (Any): Currently authenticated user with staff privileges.
            Automatically validated via JWT token. Must be an active staff member.

    Authentication:
        Requires valid JWT bearer token in Authorization header.
        Format: "Authorization: Bearer <token>"
        User must have staff role (teacher, administrator, etc.).

    Returns:
        List[Asset]: List of all asset objects containing:
            - Asset identification and metadata
            - Asset type and category
            - Current status and availability
            - Location and assignment information
            - Other asset-specific attributes

    Raises:
        401 Unauthorized: If authentication token is missing or invalid.
        403 Forbidden: If authenticated user does not have staff privileges.
        500 Internal Server Error: If database query fails.

    HTTP Status Codes:
        200 OK: Assets retrieved successfully.
        401 Unauthorized: Missing or invalid authentication credentials.
        403 Forbidden: Insufficient permissions (non-staff user).
        500 Internal Server Error: Server-side error during processing.

    Example:
        GET /api/v1/assets/
        Headers: Authorization: Bearer eyJhbGc...
        Response: [
            {
                "id": 1,
                "name": "Laptop Dell XPS 15",
                "type": "Electronics",
                "status": "Available",
                ...
            },
            ...
        ]
    """
    return db.query(Asset).all()
