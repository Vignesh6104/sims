"""
Database Initialization Script

This module initializes the SIMS database with default data and the initial superuser account.
It should be run after applying Alembic migrations to populate the database with required
seed data and create the default admin user for first-time login.

The initialization process:
1. Creates a database session
2. Calls init_db() to populate default data
3. Creates the default admin user (admin@school.com / admin)
4. Handles errors gracefully and ensures proper session cleanup

Usage:
    python run_init.py

Prerequisites:
    - Database must exist and be accessible
    - Alembic migrations must be applied (run 'alembic upgrade head')
    - Environment variables must be configured in .env file

Default Admin Credentials:
    Email: admin@school.com
    Password: admin
    (Change these credentials immediately after first login)
"""

import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db.init_db import init_db

def run_init():
    """
    Execute database initialization with default data and admin user.
    
    Creates a database session and calls init_db() to populate the database
    with initial data. Handles exceptions and ensures proper cleanup.
    
    Raises:
        Exception: If database initialization fails, prints error details
    """
    print("Running init_db manually...")
    db = SessionLocal()
    try:
        init_db(db)
        print("init_db completed successfully.")
    except Exception as e:
        print(f"Error running init_db: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_init()
