from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Date
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("hosts.id"))
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String(255), unique=True, index=True, nullable=True)
    status = Column(String, default="inactive")
    plan_details = Column(String)
    tier = Column(String(100), default="FREE")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    host = relationship("Host", back_populates="subscription")

class Ordinance(Base):
    __tablename__ = "ordinances"
    id = Column(Integer, primary_key=True, index=True)
    jurisdiction = Column(String, index=True)
    ordinance_text = Column(Text)
    embedding = Column(Vector(1536))


class QueueTask(Base):
    __tablename__ = "queue_tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, index=True)
    payload = Column(Text)
    status = Column(String, default="pending")

class PermitTransaction(Base):
    __tablename__ = "permit_transactions"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    stripe_session_id = Column(String(255), unique=True, index=True)
    payment_status = Column(String(100), default="PENDING")
    amount_paid = Column(Float, default=150.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    ota_source = Column(String(50), nullable=False)
    external_booking_id = Column(String(255), unique=True, index=True, nullable=False)
    guest_name = Column(String(255), nullable=True)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    gross_revenue = Column(Float, default=0.0)
    tax_liability = Column(Float, default=0.0)
    payout_status = Column(String(100), default="PENDING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class GuestMessage(Base):
    __tablename__ = "guest_messages"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    ota_source = Column(String(50), nullable=False)
    sender_name = Column(String(255), nullable=False)
    message_text = Column(Text, nullable=False)
    ai_suggested_reply = Column(Text, nullable=True)
    is_replied = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)




class WaitlistLead(Base):
    __tablename__ = "waitlist_leads"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    portfolio_size = Column(String(50), nullable=True)
    tier_interest = Column(String(100), default="PHASE_2_AUTOMATION")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
