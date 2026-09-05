"""password_reset_tokens — hashed single-use reset tokens (US-014)."""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid
from app.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    host_id = Column(String, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    requested_ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
