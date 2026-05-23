import os
from dotenv import load_dotenv
from sqlalchemy import text
from app.database import engine, Base

# Load environment variables
load_dotenv()

def main():
    print("Running standalone database initialization...")
    try:
        # Explicitly import all database models so they register on Base
        import app.db_models
        import app.models.memory
        import app.models.host
        import app.models.property
        import app.models.zoning
        import app.models.job
        import app.models.compliance
        import app.models.swarm
        import app.models.oauth
        import app.integrations.ota_models
        
        # Enable PostgreSQL extensions if PostgreSQL
        if "sqlite" not in str(engine.url):
            try:
                with engine.connect() as conn:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))
                    conn.commit()
                print("pgvector and btree_gist extensions verified/created.")
            except Exception as e:
                print(f"Warning: Could not create database extensions (vector, btree_gist): {e}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        import traceback
        traceback.print_exc()
        # We raise the exception to exit with non-zero code and stop startup if DB init fails
        raise e

if __name__ == "__main__":
    main()
