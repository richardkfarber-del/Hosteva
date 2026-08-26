from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.swarm import SwarmState

engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/hosteva")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

db.query(SwarmState).filter(SwarmState.ticket_id.in_(["FEAT-019", "FEAT-020"])).delete()
db.commit()
print("DB cleared")
