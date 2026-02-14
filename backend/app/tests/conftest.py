import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Set environment variables for testing
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

from app.db.base import Base
from app.main import app
from app.api.deps import get_db

# Create an in-memory SQLite engine
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db() -> Generator:
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    session = TestingSessionLocal()
    
    # Create initial admin user
    from app.crud import crud_admin
    from app.schemas.admin import AdminCreate
    admin_in = AdminCreate(
        email="testadmin@example.com",
        password="testpassword",
        full_name="Test Admin",
        department="IT",
        position="Manager"
    )
    # Check if admin already exists (in case of re-runs or shared state)
    if not crud_admin.get_admin_by_email(session, email="testadmin@example.com"):
        crud_admin.create_admin(session, admin=admin_in)

    yield session
    
    # Drop the tables
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            pass # Session is managed by the db fixture
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def admin_token(client):
    from app.core.config import settings
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "testadmin@example.com", "password": "testpassword"},
    )
    return response.json()["access_token"]
