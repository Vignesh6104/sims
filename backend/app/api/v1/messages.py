"""
Inter-user messaging system API endpoints.

This module provides RESTful endpoints for managing messages between users in the system.

Purpose:
    Enables direct communication between users through a messaging system.

Features:
    - Send messages: Users can send messages to other users in the system
    - View conversations: Retrieve message history between two specific users
    - Message history: Access all messages sent to or from the current user

Access Control:
    All endpoints require authentication. Users can only:
    - Send messages as themselves (sender is automatically set to authenticated user)
    - View their own messages and conversations they are part of
    - Access messages where they are either sender or recipient

Sender Information Handling:
    Sender metadata is automatically extracted from the authenticated user:
    - sender_id: Derived from the current user's ID
    - sender_role: Automatically detected from the user's model class (Student, Faculty, Admin, etc.)
    - sender_name: Extracted from the user's full_name attribute, defaults to "Unknown" if not available
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.message import Message, MessageCreate
from app.crud import crud_message

router = APIRouter()

@router.post("/", response_model=Message)
def send_message(
    message_in: MessageCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Send a message to another user.

    Creates a new message from the authenticated user to a specified recipient.
    The sender information is automatically extracted from the authenticated user's
    profile and cannot be spoofed.

    Args:
        message_in (MessageCreate): Message data containing:
            - recipient_id: ID of the user receiving the message
            - content: Text content of the message
            - subject (optional): Message subject line
        db (Session): Database session dependency
        current_user (Any): Currently authenticated user (automatically injected)

    Authentication:
        Requires valid JWT token. User must be active.

    Returns:
        Message: The created message object with all metadata including:
            - id: Unique message identifier
            - sender_id: Authenticated user's ID
            - sender_role: Sender's role in the system
            - sender_name: Sender's full name
            - recipient_id: Recipient's user ID
            - content: Message content
            - timestamp: Creation timestamp
            - read status

    Raises:
        HTTPException: 
            - 401 Unauthorized: If user is not authenticated
            - 403 Forbidden: If user account is inactive
            - 404 Not Found: If recipient_id does not exist
            - 422 Unprocessable Entity: If message_in validation fails

    HTTP Status Codes:
        - 200 OK: Message sent successfully
        - 401 Unauthorized: Authentication required
        - 403 Forbidden: User not active
        - 404 Not Found: Recipient not found
        - 422 Unprocessable Entity: Invalid input data
    """
    # Identify sender role by extracting the class name of the user model
    # (e.g., 'Student', 'Faculty', 'Admin') and converting to lowercase
    role = current_user.__class__.__name__.lower()
    
    # Extract sender's display name from the user's full_name attribute
    # Falls back to "Unknown" if the attribute doesn't exist
    name = getattr(current_user, "full_name", "Unknown")
    
    return crud_message.create_message(
        db=db, 
        message=message_in, 
        sender_id=str(current_user.id), 
        sender_role=role,
        sender_name=name
    )

@router.get("/", response_model=List[Message])
def read_messages(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all messages for the authenticated user.

    Returns all messages where the authenticated user is either the sender
    or the recipient. This provides a complete view of the user's message
    history across all conversations.

    Args:
        db (Session): Database session dependency
        current_user (Any): Currently authenticated user (automatically injected)

    Authentication:
        Requires valid JWT token. User must be active.

    Returns:
        List[Message]: List of all messages involving the authenticated user,
            ordered by timestamp (implementation dependent). Each message includes:
            - id: Unique message identifier
            - sender_id: ID of the message sender
            - sender_role: Role of the sender
            - sender_name: Display name of the sender
            - recipient_id: ID of the message recipient
            - content: Message content
            - timestamp: When the message was sent
            - read status and other metadata

    Raises:
        HTTPException:
            - 401 Unauthorized: If user is not authenticated
            - 403 Forbidden: If user account is inactive

    HTTP Status Codes:
        - 200 OK: Messages retrieved successfully (may be empty list)
        - 401 Unauthorized: Authentication required
        - 403 Forbidden: User not active
    """
    return crud_message.get_user_messages(db, user_id=str(current_user.id))

@router.get("/conversation/{other_user_id}", response_model=List[Message])
def read_conversation(
    other_user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve conversation history between the authenticated user and another user.

    Returns all messages exchanged between the authenticated user and the specified
    other user, providing a focused view of a single conversation thread.

    Args:
        other_user_id (str): ID of the other user in the conversation (path parameter)
        db (Session): Database session dependency
        current_user (Any): Currently authenticated user (automatically injected)

    Authentication:
        Requires valid JWT token. User must be active.

    Returns:
        List[Message]: List of messages between the two users, ordered by timestamp
            (implementation dependent). Each message includes:
            - id: Unique message identifier
            - sender_id: ID of the message sender (either current_user or other_user)
            - sender_role: Role of the sender
            - sender_name: Display name of the sender
            - recipient_id: ID of the message recipient
            - content: Message content
            - timestamp: When the message was sent
            - read status and other metadata

    Raises:
        HTTPException:
            - 401 Unauthorized: If user is not authenticated
            - 403 Forbidden: If user account is inactive
            - 404 Not Found: If other_user_id does not exist (implementation dependent)

    HTTP Status Codes:
        - 200 OK: Conversation retrieved successfully (may be empty list)
        - 401 Unauthorized: Authentication required
        - 403 Forbidden: User not active
        - 404 Not Found: Other user does not exist

    Notes:
        The conversation is filtered to only include messages where:
        - (sender = current_user AND recipient = other_user) OR
        - (sender = other_user AND recipient = current_user)
    """
    # Filter conversation to only messages between these two specific users,
    # regardless of who sent or received each message in the exchange
    return crud_message.get_conversation(db, user_a_id=str(current_user.id), user_b_id=other_user_id)
