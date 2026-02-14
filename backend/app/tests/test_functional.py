from app.core.config import settings

def test_admin_login(client):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "testadmin@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_teacher_crud(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
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

def test_student_crud(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
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

def test_classroom_crud(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
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

def test_notifications_parent(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    parent_data = {
        "email": "parent@example.com",
        "password": "parentpassword",
        "full_name": "Parent User",
        "phone_number": "1234567890"
    }
    response = client.post(f"{settings.API_V1_STR}/parents/", json=parent_data, headers=headers)
    assert response.status_code == 200
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "parent@example.com", "password": "parentpassword"},
    )
    assert response.status_code == 200
    parent_token = response.json()["access_token"]
    parent_headers = {"Authorization": f"Bearer {parent_token}"}

    client.post(f"{settings.API_V1_STR}/notifications/", json={
        "title": "Welcome", "message": "Welcome to SIMS", "recipient_role": "all"
    }, headers=headers)

    response = client.get(f"{settings.API_V1_STR}/notifications/", headers=parent_headers)
    assert response.status_code == 200
    assert any(n["title"] == "Welcome" for n in response.json())

def test_full_academic_flow(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

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
        "title": "Math Homework", "description": "Solve eq", "class_id": class_id, 
        "due_date": "2026-12-31", "subject_id": subject_id, "teacher_id": teacher_id
    }, headers=t_headers)
    assign_id = assign_res.json()["id"]

    # 6. Student login and submit
    s_token = client.post(f"{settings.API_V1_STR}/auth/login", data={"username": "student2@example.com", "password": "pass"}).json()["access_token"]
    s_headers = {"Authorization": f"Bearer {s_token}"}
    
    from unittest.mock import patch
    with patch("cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {"secure_url": "http://test.com/file.pdf"}
        files = {"file": ("test.pdf", b"content", "application/pdf")}
        data = {"assignment_id": assign_id}
        client.post(f"{settings.API_V1_STR}/assignments/submissions", data=data, files=files, headers=s_headers)

    # 7. Mark entry
    exam_res = client.post(f"{settings.API_V1_STR}/exams/", json={
        "name": "Final", "date": "2026-12-01", "term": "Fall"
    }, headers=t_headers)
    exam_id = exam_res.json()["id"]

    mark_res = client.post(f"{settings.API_V1_STR}/marks/", json={
        "student_id": student_id, "exam_id": exam_id, "subject": "Math", "score": 95, "max_score": 100
    }, headers=t_headers)
    assert mark_res.status_code == 200
    
    # 8. Fee payment
    fee_struct_res = client.post(f"{settings.API_V1_STR}/fees/structures", json={
        "class_id": class_id, "amount": 1000, "description": "Tuition", "due_date": "2026-01-01", "academic_year": "2026"
    }, headers=headers)
    fee_struct = fee_struct_res.json()
    
    pay_res = client.post(f"{settings.API_V1_STR}/fees/payments", json={
        "student_id": student_id, "fee_structure_id": fee_struct["id"], 
        "amount_paid": 1000, "status": "paid", "payment_date": "2026-01-01"
    }, headers=headers)
    assert pay_res.status_code == 200
