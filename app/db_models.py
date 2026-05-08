from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    subscription = relationship("Subscription", back_populates="user", uselist=False)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_customer_id = Column(String, unique=True, index=True)
    status = Column(String, default="inactive")
    plan_details = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user = relationship("User", back_populates="subscription")

class Ordinance(Base):
    __tablename__ = "ordinances"
    id = Column(Integer, primary_key=True, index=True)
    jurisdiction = Column(String, index=True)
    ordinance_text = Column(Text)
    embedding = Column(Vector(768))

class QueueTask(Base):
    __tablename__ = "queue_tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, index=True)
    payload = Column(Text)
    status = Column(String, default="pending")
