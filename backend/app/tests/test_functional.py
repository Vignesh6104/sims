import os

# Set dummy environment variables for testing
os.environ["PROJECT_NAME"] = "Test SIMS"
os.environ["API_V1_STR"] = "/api/v1"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "testsecret"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["CLOUDINARY_CLOUD_NAME"] = "test"
os.environ["CLOUDINARY_API_KEY"] = "test"
os.environ["CLOUDINARY_API_SECRET"] = "test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db
from app.db.session import Base
from app.core.config import settings

# Setup Test Database (SQLite in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Create initial admin
    from app.crud import crud_admin
    from app.schemas.admin import AdminCreate
    db = TestingSessionLocal()
    admin_in = AdminCreate(
        email="testadmin@example.com",
        password="testpassword",
        full_name="Test Admin",
        department="IT",
        position="Manager"
    )
    crud_admin.create_admin(db, admin=admin_in)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def test_admin_login():
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "testadmin@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    return data["access_token"]

def test_teacher_crud():
    token = test_admin_login()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Teacher
    teacher_data = {
        "email": "teacher@example.com",
        "password": "teacherpassword",
        "full_name": "John Teacher",
        "qualification": "PhD",
        "subject_specialization": "Mathematics"
    }
    response = client.post(f"{settings.API_V1_STR}/teachers/", json=teacher_data, headers=headers)
    assert response.status_code == 200
    teacher_id = response.json()["id"]
    
    # Read Teachers
    response = client.get(f"{settings.API_V1_STR}/teachers/", headers=headers)
    assert response.status_code == 200
    assert any(t["email"] == "teacher@example.com" for t in response.json())
    
    # Update Teacher
    update_data = {"full_name": "John Updated"}
    response = client.put(f"{settings.API_V1_STR}/teachers/{teacher_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "John Updated"
    
    # Delete Teacher
    response = client.delete(f"{settings.API_V1_STR}/teachers/{teacher_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"{settings.API_V1_STR}/teachers/{teacher_id}", headers=headers)
    assert response.status_code == 404

def test_student_crud():
    token = test_admin_login()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Student
    student_data = {
        "email": "student@example.com",
        "password": "studentpassword",
        "full_name": "Jane Student",
        "roll_number": "S001",
        "address": "123 Street"
    }
    response = client.post(f"{settings.API_V1_STR}/students/", json=student_data, headers=headers)
    assert response.status_code == 200
    student_id = response.json()["id"]
    
    # Read Student
    response = client.get(f"{settings.API_V1_STR}/students/{student_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Jane Student"
    
    # Delete Student
    response = client.delete(f"{settings.API_V1_STR}/students/{student_id}", headers=headers)
    assert response.status_code == 200

def test_classroom_crud():
    token = test_admin_login()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create ClassRoom
    class_data = {
        "name": "Class 10A",
        "section": "A",
        "capacity": 30
    }
    response = client.post(f"{settings.API_V1_STR}/class_rooms/", json=class_data, headers=headers)
    assert response.status_code == 200
    class_id = response.json()["id"]
    
    # Get ClassRoom
    response = client.get(f"{settings.API_V1_STR}/class_rooms/{class_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Class 10A"

def test_notifications_parent():
    # 1. Create Parent
    token = test_admin_login()
    headers = {"Authorization": f"Bearer {token}"}
    parent_data = {
        "email": "parent@example.com",
        "password": "parentpassword",
        "full_name": "Parent User",
        "phone_number": "1234567890"
    }
    # Using parent registration or admin creation
    response = client.post(f"{settings.API_V1_STR}/parents/", json=parent_data, headers=headers)
    assert response.status_code == 200
    parent_id = response.json()["id"]

    # 2. Login as Parent
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "parent@example.com", "password": "parentpassword"},
    )
    assert response.status_code == 200
    parent_token = response.json()["access_token"]
    parent_headers = {"Authorization": f"Bearer {parent_token}"}

    # 3. Admin sends notification to all
    notif_data = {
        "title": "Welcome",
        "message": "Welcome to SIMS",
        "recipient_role": "all"
    }
    client.post(f"{settings.API_V1_STR}/notifications/", json=notif_data, headers=headers)

    # 4. Parent checks notifications
    response = client.get(f"{settings.API_V1_STR}/notifications/", headers=parent_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["title"] == "Welcome"

def test_full_academic_flow():
    token = test_admin_login()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Teacher
    teacher_res = client.post(f"{settings.API_V1_STR}/teachers/", json={
        "email": "teacher2@example.com", "password": "pass", "full_name": "T2"
    }, headers=headers)
    teacher_id = teacher_res.json()["id"]

    # 2. Login as Teacher
    t_token = client.post(f"{settings.API_V1_STR}/auth/login", data={"username": "teacher2@example.com", "password": "pass"}).json()["access_token"]
    t_headers = {"Authorization": f"Bearer {t_token}"}

    # 3. Create Class
    class_res = client.post(f"{settings.API_V1_STR}/class_rooms/", json={
        "name": "Flow Class", "section": "B", "teacher_id": teacher_id
    }, headers=headers)
    class_id = class_res.json()["id"]

    # 4. Create Student in that class
    student_res = client.post(f"{settings.API_V1_STR}/students/", json={
        "email": "student2@example.com", "password": "pass", "full_name": "S2", "class_id": class_id
    }, headers=headers)
    student_id = student_res.json()["id"]

    # 4.5 Create Subject
    sub_res = client.post(f"{settings.API_V1_STR}/subjects/", json={
        "name": "Math", "code": "MATH101", "description": "Math class"
    }, headers=headers)
    subject_id = sub_res.json()["id"]

    # 5. Teacher creates Assignment
    assign_res = client.post(f"{settings.API_V1_STR}/assignments/", json={
        "title": "Math Homework", 
        "description": "Solve eq", 
        "class_id": class_id, 
        "due_date": "2026-12-31",
        "subject_id": subject_id,
        "teacher_id": teacher_id
    }, headers=t_headers)
    assert assign_res.status_code == 200
    assign_id = assign_res.json()["id"]

    # 6. Student login and submit (Mocking Cloudinary)
    s_token = client.post(f"{settings.API_V1_STR}/auth/login", data={"username": "student2@example.com", "password": "pass"}).json()["access_token"]
    s_headers = {"Authorization": f"Bearer {s_token}"}
    
    from unittest.mock import patch
    with patch("cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {"secure_url": "http://test.com/file.pdf"}
        
        files = {"file": ("test.pdf", b"content", "application/pdf")}
        data = {"assignment_id": assign_id}
        sub_res = client.post(f"{settings.API_V1_STR}/assignments/submissions", data=data, files=files, headers=s_headers)
        assert sub_res.status_code == 200

    # 7. Teacher marks the student
    # Need an exam first
    exam_res = client.post(f"{settings.API_V1_STR}/exams/", json={
        "name": "Final", "date": "2026-12-01", "term": "Fall"
    }, headers=t_headers)
    exam_id = exam_res.json()["id"]

    mark_res = client.post(f"{settings.API_V1_STR}/marks/", json={
        "student_id": student_id, "exam_id": exam_id, "subject": "Math", "score": 95, "max_score": 100
    }, headers=t_headers)
    assert mark_res.status_code == 200
    
    # 8. Admin records fee payment
    # Need fee structure
    fee_struct_res = client.post(f"{settings.API_V1_STR}/fees/structures", json={
        "class_id": class_id, "amount": 1000, "description": "Tuition", "due_date": "2026-01-01", "academic_year": "2026"
    }, headers=headers)
    assert fee_struct_res.status_code == 200
    fee_struct = fee_struct_res.json()
    
    # Payment recording is currently superuser only in the API
    pay_res = client.post(f"{settings.API_V1_STR}/fees/payments", json={
        "student_id": student_id, 
        "fee_structure_id": fee_struct["id"], 
        "amount_paid": 1000, 
        "status": "paid",
        "payment_date": "2026-01-01"
    }, headers=headers)
    assert pay_res.status_code == 200
