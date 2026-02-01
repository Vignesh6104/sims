import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db.init_db import init_db

def run_init():
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
