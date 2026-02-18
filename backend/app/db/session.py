"""
Database Session Management

This module configures the SQLAlchemy engine and session factory for the SIMS application.
It handles database-specific connection arguments and connection pool settings.

Database Support:
    - PostgreSQL (recommended for production)
    - SQLite (for development/testing)

Connection Pool Features:
    - pool_pre_ping: Validates connections before use (handles stale connections)
    - check_same_thread: Disabled for SQLite to allow FastAPI async operations

Components:
    engine: SQLAlchemy engine connected to configured database
    SessionLocal: Session factory for creating database sessions
    Base: Declarative base class for all ORM models

Usage:
    from app.db.session import SessionLocal, Base
    
    # Create a session
    db = SessionLocal()
    try:
        # Perform database operations
        db.query(Model).all()
        db.commit()
    finally:
        db.close()
    
    # In FastAPI endpoints (use dependency injection instead)
    from app.api.deps import get_db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite requires check_same_thread=False for async FastAPI compatibility
# PostgreSQL and other databases don't need this parameter
connect_args = {"check_same_thread": False} if "sqlite" in settings.SQLALCHEMY_DATABASE_URI else {}

# Create database engine with connection pooling
# pool_pre_ping=True ensures stale connections are recycled automatically
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    connect_args=connect_args,
    pool_pre_ping=True  # Prevents "connection already closed" errors
)

# Session factory for creating database sessions
# autocommit=False: Explicit commit required (prevents accidental data changes)
# autoflush=False: Manual flush control for better transaction management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for all ORM model classes
# All models inherit from this class to be mapped to database tables
Base = declarative_base()
