from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, Integer, CheckConstraint, text, text, Index
from sqlalchemy.dialects.postgresql import UUID, TSTZRANGE
from app.database import Base
from sqlalchemy.sql import func
import uuid

class MunicipalCode(Base):
    __tablename__ = "municipal_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    municipality_name = Column(String(100), nullable=False)
    ordinance_number = Column(String(50), nullable=False)
    str_prohibited = Column(Boolean, default=False)
    max_occupancy_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('length(municipality_name) > 0', name='chk_mun_name_length'),
        CheckConstraint("ordinance_number ~ '^[A-Z0-9-]+$'", name='chk_ordinance_format'),
    )

class PropertyCompliance(Base):
    __tablename__ = "property_compliance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(String, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    municipal_code_id = Column(UUID(as_uuid=True), ForeignKey('municipal_codes.id', ondelete='RESTRICT'), nullable=False)
    is_compliant = Column(Boolean, nullable=False, default=False)
    violation_notes = Column(String(500), nullable=True)
    valid_period = Column(TSTZRANGE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
