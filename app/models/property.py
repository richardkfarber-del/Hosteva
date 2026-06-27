from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=True)
    property_type = Column(String, nullable=True)
    hoa_status = Column(Boolean, default=False)
    zoning_status = Column(String, default="Pending")
    image_url = Column(String, nullable=True)
    required_permits = Column(String, nullable=True)
    local_restrictions = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    airbnb_ical_import_url = Column(String, nullable=True)
    vrbo_ical_import_url = Column(String, nullable=True)
    hosteva_ical_export_token = Column(String, unique=True, nullable=True)

