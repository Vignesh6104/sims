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
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(admins.router, prefix=f"{settings.API_V1_STR}/admins", tags=["admins"])
app.include_router(students.router, prefix=f"{settings.API_V1_STR}/students", tags=["students"])
app.include_router(teachers.router, prefix=f"{settings.API_V1_STR}/teachers", tags=["teachers"])
app.include_router(parents.router, prefix=f"{settings.API_V1_STR}/parents", tags=["parents"])
app.include_router(attendance.router, prefix=f"{settings.API_V1_STR}/attendance", tags=["attendance"])
app.include_router(marks.router, prefix=f"{settings.API_V1_STR}/marks", tags=["marks"])
app.include_router(class_rooms.router, prefix=f"{settings.API_V1_STR}/class_rooms", tags=["class_rooms"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(subjects.router, prefix=f"{settings.API_V1_STR}/subjects", tags=["subjects"])
app.include_router(exams.router, prefix=f"{settings.API_V1_STR}/exams", tags=["exams"])
app.include_router(fees.router, prefix=f"{settings.API_V1_STR}/fees", tags=["fees"])
app.include_router(timetable.router, prefix=f"{settings.API_V1_STR}/timetable", tags=["timetable"])
app.include_router(assignments.router, prefix=f"{settings.API_V1_STR}/assignments", tags=["assignments"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(events.router, prefix=f"{settings.API_V1_STR}/events", tags=["events"])
app.include_router(library.router, prefix=f"{settings.API_V1_STR}/library", tags=["library"])

@app.on_event("startup")
def on_startup():
    from app.db.session import engine
    from app.db.base import Base
    from app.db.init_db import init_db
    from app.db.session import SessionLocal

    # Create tables (simple approach for dev without Alembic running)
    Base.metadata.create_all(bind=engine)
    
    # Init DB (create superuser)
    db = SessionLocal()
    init_db(db)
    db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the School Information Management System API"}
