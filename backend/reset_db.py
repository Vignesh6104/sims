"""
Database Reset Utility

This module provides functionality to completely reset the SIMS database by dropping
all tables, custom ENUM types, and the Alembic version tracking table. This is a
destructive operation intended for development and testing purposes only.

WARNING: This script will delete ALL data in the database. Use with extreme caution.
         Never run this in a production environment.

The reset process:
1. Drops all application tables using CASCADE to handle foreign key constraints
2. Removes custom PostgreSQL ENUM types (e.g., attendancestatus)
3. Drops the alembic_version table to allow fresh migrations
4. Handles errors gracefully for each operation

After running this script, you must:
1. Re-apply migrations: alembic upgrade head
2. Re-initialize data: python run_init.py

Usage:
    python reset_db.py

Prerequisites:
    - Database connection must be configured in .env
    - User must have DROP TABLE privileges
    - Confirm you have a backup if this is not a disposable development database
"""

import sys
import os
from sqlalchemy import create_engine, text

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.config import settings

def reset_database():
    """
    Drop all database tables and ENUM types for a clean slate.
    
    Executes a series of DROP TABLE CASCADE statements to remove all application
    tables, followed by custom type cleanup. Each operation is attempted
    individually with error handling to ensure partial completion is possible.
    
    Tables Dropped:
        - All user tables (admins, teachers, students, parents)
        - Academic tables (marks, attendance, exams, subjects, classrooms)
        - Supporting tables (assignments, submissions, notifications, events, etc.)
        - System tables (alembic_version)
    
    ENUM Types Dropped:
        - attendancestatus and other custom enums
    
    Warning:
        This is a destructive operation. All data will be permanently lost.
        There is no undo functionality.
    """
    print(f"Connecting to: {settings.SQLALCHEMY_DATABASE_URI}")
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    with engine.connect() as connection:
        # Disable foreign key checks to allow dropping tables in any order (for Postgres CASCADE handles this usually, but good practice)
        # Actually in Postgres, DROP SCHEMA public CASCADE; CREATE SCHEMA public; is the nuclear option.
        # But let's try dropping individual tables reflecting the Base metadata or just the alembic_version table.
        
        print("Dropping alembic_version table...")
        try:
            connection.execute(text("DROP TABLE IF EXISTS alembic_version;"))
            connection.commit()
            print("Dropped alembic_version.")
        except Exception as e:
            print(f"Error dropping alembic_version: {e}")

        # List of all tables to drop
        tables = [
            'marks', 'attendance', 'submissions', 'assignments', 'students', 
            'classrooms', 'teachers', 'admins', 'exams', 'subjects', 
            'notifications', 'events', 'borrow_records', 'books', 'parents',
            'fee_payments', 'fee_structures', 'timetables', 'users', 'alembic_version'
        ]
        
        for table in tables:
            try:
                print(f"Dropping table {table}...")
                connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                connection.commit()
            except Exception as e:
                print(f"Error dropping {table}: {e}")
                
        # Drop ENUM types
        try:
            print("Dropping ENUM type attendancestatus...")
            connection.execute(text("DROP TYPE IF EXISTS attendancestatus;"))
            connection.commit()
        except Exception as e:
            print(f"Error dropping enum: {e}")
                
    print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
