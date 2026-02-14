from app.core.config import settings
from app.core import security

def test_access_and_refresh_token_logic(client):
    # Need to create a user for this test or use the admin
    # Let's create a specific user for token testing to match original logic
    # But since we have a clean DB, we can just use the admin or create a new one.
    # The original test created 'token_test@example.com' in setup_db.
    # Our shared conftest creates 'testadmin@example.com'.
    
    # Let's create the token_test user here to keep it isolated or just use a new one
    from app.crud import crud_admin
    from app.schemas.admin import AdminCreate
    from app.db.base import Base
    
    # We can't easily access the db session here unless we ask for 'db' fixture
    # But 'client' fixture is already overriding get_db.
    # So we can just create via API or assumes it works.
    
    # Let's try to register or just use the existing admin?
    # The original test checked email "token_test@example.com".
    # We can adapt to use "testadmin@example.com".
    
    login_data = {"username": "testadmin@example.com", "password": "testpassword"}
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    old_access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    
    headers = {"Authorization": f"Bearer {old_access_token}"}
    response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "testadmin@example.com"
    
    refresh_payload = {"refresh_token": refresh_token}
    response = client.post(f"{settings.API_V1_STR}/auth/refresh", json=refresh_payload)
    
    assert response.status_code == 200
    new_data = response.json()
    assert "access_token" in new_data
    new_access_token = new_data["access_token"]
    assert new_access_token != old_access_token
    
    new_headers = {"Authorization": f"Bearer {new_access_token}"}
    response = client.get(f"{settings.API_V1_STR}/auth/me", headers=new_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "testadmin@example.com"

def test_refresh_token_invalid_role(client):
    invalid_refresh_token = security.create_refresh_token(subject="fake_id", role="hacker")
    refresh_payload = {"refresh_token": invalid_refresh_token}
    
    response = client.post(f"{settings.API_V1_STR}/auth/refresh", json=refresh_payload)
    assert response.status_code == 404
