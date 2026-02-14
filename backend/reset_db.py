import sys
import os
from sqlalchemy import create_engine, text

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.config import settings

def reset_database():
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
