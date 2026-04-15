import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import text
from app.database import engine, Base
import app.models.swarm

def init_swarm_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Swarm Database initialization successful. vector extension and Swarm models created.")

if __name__ == "__main__":
    init_swarm_db()
