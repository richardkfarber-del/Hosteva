from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base # Assumes standard declarative base

# Placeholder import for the Black Panther mandated Vibranium Encryption Standard
# TODO: Implement actual VibraniumEncryptedString in security module
from sqlalchemy import String as VibraniumEncryptedString 

class OtaIntegration(Base):
    """
    OTA Integration model for storing platform connections.
    Mandates VibraniumEncryptedString for all OAuth tokens.
    """
    __tablename__ = "ota_integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False) 
    platform_name = Column(String, index=True, nullable=False) # e.g., 'airbnb', 'vrbo'
    
    # Vibranium Encryption Standard enforced
    access_token = Column(VibraniumEncryptedString, nullable=False)
    refresh_token = Column(VibraniumEncryptedString, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    listing_id = Column(Integer, ForeignKey("hosteva_listings.id"))
    listing = relationship("HostevaListing", back_populates="integrations")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HostevaListing(Base):
    """
    Unified Hosteva Listing model representing the core property asset.
    """
    __tablename__ = "hosteva_listings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    property_address = Column(String, nullable=False)
    compliance_status = Column(String, default="pending")
    base_price = Column(Float, nullable=True)
    
    integrations = relationship("OtaIntegration", back_populates="listing", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())