from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from app.database import Base

class Ordinance(Base):
    __tablename__ = "ordinances"
    id = Column(Integer, primary_key=True, index=True)
    jurisdiction = Column(String, index=True)
    ordinance_text = Column(Text)
    embedding = Column(Vector(768))
