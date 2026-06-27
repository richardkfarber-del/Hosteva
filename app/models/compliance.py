from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, Integer, CheckConstraint, text, Index, Float, UniqueConstraint, Text
from app.database import Base
from sqlalchemy.sql import func
import uuid
import os

db_url = os.environ.get("INTERNAL_DATABASE_URL") or os.environ.get("DATABASE_URL", "")
is_sqlite = "sqlite" in db_url or not db_url

if is_sqlite:
    from sqlalchemy.types import String as TSTZRANGE
    from sqlalchemy.dialects.postgresql import UUID
else:
    from sqlalchemy.dialects.postgresql import UUID, TSTZRANGE

class MunicipalCode(Base):
    __tablename__ = "municipal_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    municipality_name = Column(String(100), nullable=False)
    ordinance_number = Column(String(50), nullable=False)
    str_prohibited = Column(Boolean, default=False)
    max_occupancy_limit = Column(Integer, nullable=True)
    stay_restriction_days = Column(Integer, nullable=True, default=None)
    max_rentals_per_year = Column(Integer, nullable=True, default=None)
    requires_permit = Column(Boolean, default=False, nullable=True)
    permit_name = Column(String(100), nullable=True, default=None)
    source_url = Column(String(255), nullable=True, default=None)
    tax_rate = Column(Float, nullable=True, default=None)
    is_allowed = Column(Boolean, default=True, nullable=True)
    zoning_code = Column(String(50), nullable=True, default=None)
    property_type = Column(String(50), nullable=True, default=None)
    rejection_reason = Column(String(255), nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- NEW FIELDS FOR PHASE 1 JURISDICTIONS SPREADSHEET ---
    jurisdiction_type = Column(String(50), nullable=True)
    str_permitted_raw = Column(String(100), nullable=True)
    permit_required_raw = Column(String(50), nullable=True)
    minimum_stay_requirement = Column(String(255), nullable=True)
    occupancy_limits = Column(String(255), nullable=True)
    tax_rate_registration_fee = Column(String(255), nullable=True)
    last_verified_date = Column(Date, nullable=True)

    if is_sqlite:
        __table_args__ = (
            CheckConstraint('length(municipality_name) > 0', name='chk_mun_name_length'),
            UniqueConstraint('municipality_name', 'jurisdiction_type', name='uq_municipal_codes_name_type'),
        )
    else:
        __table_args__ = (
            CheckConstraint('length(municipality_name) > 0', name='chk_mun_name_length'),
            CheckConstraint("ordinance_number ~ '^[A-Z0-9-]+$'", name='chk_ordinance_format'),
            UniqueConstraint('municipality_name', 'jurisdiction_type', name='uq_municipal_codes_name_type'),
        )

class HOARule(Base):
    __tablename__ = "hoa_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hoa_name = Column(String(150), nullable=False, index=True)
    location = Column(String(150), nullable=False)
    str_permitted = Column(String(100), nullable=False)
    minimum_lease_stay = Column(String(100), nullable=True)
    rules_available = Column(Boolean, default=True)
    official_website = Column(String(250), nullable=True)
    last_confirmed_date = Column(Date, nullable=True)
    key_rules_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('hoa_name', 'location', name='uq_hoa_rules_name_location'),
    )


class PropertyCompliance(Base):
    __tablename__ = "property_compliance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(String, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    municipal_code_id = Column(UUID(as_uuid=True), ForeignKey('municipal_codes.id', ondelete='RESTRICT'), nullable=False)
    is_compliant = Column(Boolean, nullable=False, default=False)
    status = Column(String(50), nullable=True, default="PENDING")
    rejection_notes = Column(String(500), nullable=True)
    violation_notes = Column(String(500), nullable=True)
    valid_period = Column(TSTZRANGE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_file_url = Column(String(500), nullable=True)
    ocr_metadata_json = Column(Text, nullable=True)
    verification_notes = Column(Text, nullable=True)
    task_name = Column(String(255), nullable=True)


    if is_sqlite:
        # SQLite doesn't support gist indexes or range types, so we don't define table args / index
        pass
    else:
        __table_args__ = (
            Index('ix_property_compliance_valid_period', 'property_id', 'valid_period', postgresql_using='gist'),
        )

class Region(Base):
    __tablename__ = "regions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    locality = Column(String(100))
    admin_area = Column(String(50))

class ZoningCode(Base):
    __tablename__ = "zoning_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"))
    code_name = Column(String(50))
    description = Column(String(200))

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zoning_id = Column(UUID(as_uuid=True), ForeignKey("zoning_codes.id"))
    eligibility_status = Column(String(50))
    is_str_allowed = Column(Boolean)
    requires_permit = Column(Boolean)
    min_stay_days = Column(Integer)
    primary_residence_required = Column(Boolean)
    plain_english_conditions = Column(String(500))
    permit_application_url = Column(String(200))
    ordinance_reference_url = Column(String(200))
