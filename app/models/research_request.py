"""SP-011 research_requests — internal Free Audit miss queue (draft only)."""
from sqlalchemy import Column, String, DateTime, Integer, Text, UniqueConstraint
from sqlalchemy.sql import func
import uuid
import os

from app.database import Base

db_url = os.environ.get("INTERNAL_DATABASE_URL") or os.environ.get("DATABASE_URL", "")
is_sqlite = "sqlite" in db_url or not db_url

from sqlalchemy.types import TypeDecorator, String as StringType
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


class UUID(TypeDecorator):
    impl = StringType
    cache_ok = True

    def __init__(self, as_uuid=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        return dialect.type_descriptor(StringType(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except Exception:
            return value


class ResearchRequest(Base):
    __tablename__ = "research_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jurisdiction_key = Column(String(255), nullable=False, index=True)
    state = Column(String(10), nullable=False)
    municipality_name = Column(String(150), nullable=False)
    jurisdiction_type = Column(String(50), nullable=True)
    sample_address = Column(String(255), nullable=True)
    host_id = Column(String, nullable=True)
    status = Column(String(50), nullable=False, default="queued", index=True)
    # queued | in_progress | draft_ready | rejected | promoted
    trigger_reason = Column(String(100), nullable=True)
    priority = Column(Integer, nullable=False, default=100)
    hit_count = Column(Integer, nullable=False, default=1)
    draft_municipal_code_id = Column(UUID(as_uuid=True), nullable=True)
    draft_payload = Column(Text, nullable=True)  # JSON text; never auto-Covered
    worker_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("jurisdiction_key", name="uq_research_requests_jurisdiction_key"),
    )
