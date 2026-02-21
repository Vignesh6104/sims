import uuid
from sqlalchemy import Column, String, Integer, LargeBinary, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    user_role = Column(String, nullable=False) # e.g., 'admin', 'teacher', 'student', 'parent'
    credential_id = Column(String, unique=True, index=True, nullable=False)
    public_key = Column(String, nullable=False)
    sign_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
