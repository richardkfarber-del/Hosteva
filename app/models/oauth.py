from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
from app.database import Base

class OAuthConnection(Base):
    __tablename__ = "oauth_connections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=True) # hosts table is used instead of users
    platform = Column(String, nullable=False)
    platform_account_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    scopes = Column(String, nullable=True) # or ARRAY(String) if using postgres specific
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('tenant_id', 'platform', 'platform_account_id', name='uq_oauth_connection'),
    )

class PropertyListing(Base):
    __tablename__ = "property_listings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False)
    property_id = Column(String, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    platform_name = Column(String, nullable=False)
    external_listing_id = Column(String, nullable=True)
    external_url = Column(String, nullable=True)
    status = Column(String, default="pending")
    sync_status = Column(String, default="in_sync")
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    error_log = Column(String, nullable=True) # JSON stored as string for simplicity across DBs or JSONB for pg
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('property_id', 'platform_name', name='uq_property_listing'),
    )
