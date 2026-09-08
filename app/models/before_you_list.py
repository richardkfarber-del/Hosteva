"""PL-12 / TE-012 — persisted Before You List checklist item state (Free Covered carve-out)."""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
import uuid
from app.database import Base


class BeforeYouListItem(Base):
    __tablename__ = "before_you_list_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id = Column(
        String,
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_key = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)
    is_complete = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("property_id", "item_key", name="uq_byl_property_item_key"),
    )
