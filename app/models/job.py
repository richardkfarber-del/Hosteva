from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.database import Base

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, index=True)
    payload = Column(JSON)
    status = Column(String, default='PENDING', index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
