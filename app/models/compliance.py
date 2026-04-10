from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Region(Base):
    __tablename__ = "regions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    locality = Column(String(255), nullable=False)
    admin_area = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('locality', 'admin_area', name='uq_region_locality_admin'),)
    
    zoning_codes = relationship("ZoningCode", back_populates="region", cascade="all, delete-orphan")

class ZoningCode(Base):
    __tablename__ = "zoning_codes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    region_id = Column(String, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False)
    code_name = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('region_id', 'code_name', name='uq_zoning_region_code'),)
    
    region = relationship("Region", back_populates="zoning_codes")
    compliance_rules = relationship("ComplianceRule", back_populates="zoning_code", cascade="all, delete-orphan")

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    zoning_id = Column(String, ForeignKey("zoning_codes.id", ondelete="CASCADE"), nullable=False)
    eligibility_status = Column(String(10), nullable=False)
    is_str_allowed = Column(Boolean, nullable=False)
    requires_permit = Column(Boolean, default=False)
    min_stay_days = Column(Integer, default=1)
    primary_residence_required = Column(Boolean, default=False)
    plain_english_conditions = Column(Text)
    permit_application_url = Column(Text)
    ordinance_reference_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('zoning_id', name='uq_compliance_zoning'),)
    
    zoning_code = relationship("ZoningCode", back_populates="compliance_rules")