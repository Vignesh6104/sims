import pytest
from app.core.config import settings

@pytest.fixture(scope="module")
def teacher_token(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    teacher_data = {
        "email": "testteacher@example.com",
        "password": "teacherpassword",
        "full_name": "Test Teacher",
        "qualification": "MA",
        "subject_specialization": "History"
    }
    client.post(f"{settings.API_V1_STR}/teachers/", json=teacher_data, headers=headers)
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "testteacher@example.com", "password": "teacherpassword"},
    )
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def student_token(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    student_data = {
        "email": "teststudent@example.com",
        "password": "studentpassword",
        "full_name": "Test Student",
        "roll_number": "S999"
    }
    client.post(f"{settings.API_V1_STR}/students/", json=student_data, headers=headers)
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "teststudent@example.com", "password": "studentpassword"},
    )
    return response.json()["access_token"]

def test_leave_application(client, student_token, admin_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    leave_data = {
        "start_date": "2026-03-01",
        "end_date": "2026-03-05",
        "leave_type": "SICK",
        "reason": "Feeling unwell"
    }
    response = client.post(f"{settings.API_V1_STR}/leaves/", json=leave_data, headers=headers)
    assert response.status_code == 200
    leave_id = response.json()["id"]
    assert response.json()["status"] == "PENDING"

    # Admin approves
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(
        f"{settings.API_V1_STR}/leaves/{leave_id}", 
        json={"status": "APPROVED"}, 
        headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"

def test_feedback_system(client, student_token, admin_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    feedback_data = {
        "subject": "Library Books",
        "description": "Need more science books",
        "priority": "MEDIUM"
    }
    response = client.post(f"{settings.API_V1_STR}/feedbacks/", json=feedback_data, headers=headers)
    assert response.status_code == 200
    feedback_id = response.json()["id"]

    # Admin responds
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(
        f"{settings.API_V1_STR}/feedbacks/{feedback_id}", 
        json={"admin_response": "We will order them soon.", "status": "RESOLVED"}, 
        headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "RESOLVED"

def test_quizzes(client, teacher_token, student_token, admin_token):
    # Need a classroom and subject for quiz
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create ClassRoom
    class_res = client.post(f"{settings.API_V1_STR}/class_rooms/", json={"name": "Test Class"}, headers=admin_headers)
    class_id = class_res.json()["id"]
    
    # Create Subject
    sub_res = client.post(f"{settings.API_V1_STR}/subjects/", json={"name": "Test Subject", "code": "TS101"}, headers=admin_headers)
    subject_id = sub_res.json()["id"]

    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    quiz_data = {
        "title": "History Quiz",
        "description": "Short quiz on history",
        "class_id": class_id,
        "subject_id": subject_id,
        "questions_data": [
            {
                "question": "Who was the first president?",
                "options": ["Washington", "Jefferson", "Adams"],
                "correct_answer": 0,
                "points": 10
            }
        ]
    }
    response = client.post(f"{settings.API_V1_STR}/quizzes/", json=quiz_data, headers=teacher_headers)
    assert response.status_code == 200
    quiz_id = response.json()["id"]

    # Student submits
    student_headers = {"Authorization": f"Bearer {student_token}"}
    submission_data = {
        "quiz_id": quiz_id,
        "answers": [0]
    }
    response = client.post(f"{settings.API_V1_STR}/quizzes/submit", json=submission_data, headers=student_headers)
    assert response.status_code == 200
    assert response.json()["score"] == 10.0

def test_assets_and_salaries(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Check assets (might be empty but should return 200)
    response = client.get(f"{settings.API_V1_STR}/assets/", headers=headers)
    assert response.status_code == 200
    
    # Check salaries
    response = client.get(f"{settings.API_V1_STR}/salaries/salaries", headers=headers)
    assert response.status_code == 200
