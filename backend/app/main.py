from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import cloudinary
from app.core.config import settings
from app.api.v1 import admins, auth, students, teachers, attendance, marks, class_rooms, dashboard, subjects, exams, fees, timetable, assignments, notifications, events, library, parents

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Initialize Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

# Ensure uploads directory exists for legacy support
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Serve uploads statically for legacy support
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "https://sims-pied-six.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
# ... (all other routers)

# Database Initialization
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.init_db import init_db

# Create tables and initialize admin user
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()
    print("Database initialized successfully.")
except Exception as e:
    print(f"Database initialization failed: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the School Information Management System API"}
