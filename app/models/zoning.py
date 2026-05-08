from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Boolean, Date, Integer, JSON, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class LandUseType(Base):
    __tablename__ = "land_use_types"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ZoningDistrict(Base):
    __tablename__ = "zoning_districts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ComplianceRuleType(Base):
    __tablename__ = "compliance_rule_types"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    unit_of_measure = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ZoningRegulation(Base):
    __tablename__ = "zoning_regulations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    zoning_district_id = Column(String, ForeignKey("zoning_districts.id", ondelete="CASCADE"), nullable=False)
    land_use_type_id = Column(String, ForeignKey("land_use_types.id", ondelete="CASCADE"), nullable=False)
    rule_type_id = Column(String, ForeignKey("compliance_rule_types.id", ondelete="CASCADE"), nullable=False)
    min_value = Column(Numeric(12,2))
    max_value = Column(Numeric(12,2))
    is_permitted = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)
    notes = Column(Text)
    valid_from = Column(Date, nullable=False, server_default=func.current_date())
    valid_to = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ComplianceReport(Base):
    __tablename__ = "compliance_reports"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    report_number = Column(Integer, primary_key=False, autoincrement=True) # Note: primary_key=True or use Serial in Postgres
    property_id = Column(String, nullable=False)
    zoning_district_id = Column(String, ForeignKey("zoning_districts.id"), nullable=False)
    proposed_land_use_id = Column(String, ForeignKey("land_use_types.id"), nullable=False)
    is_compliant = Column(Boolean, nullable=False, default=False)
    issues = Column(JSON) # Detailed JSON on non-compliance
    analyst_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
