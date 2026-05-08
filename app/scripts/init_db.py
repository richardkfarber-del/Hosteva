from sqlalchemy import text
from app.database import engine, Base
import app.db_models

def init_db():
    # Enable the pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialization successful. Tables and extensions created.")

if __name__ == "__main__":
    init_db()
