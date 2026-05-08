from sqlalchemy import Column, String, Integer, JSON, DateTime, Text
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime

class SwarmState(Base):
    __tablename__ = "swarm_states"
    
    ticket_id = Column(String, primary_key=True)
    status = Column(String)
    payload = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SwarmMemory(Base):
    __tablename__ = "swarm_memories"
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    timestamp = Column(DateTime)
    content = Column(Text)
    embedding = Column(Vector(1536))
