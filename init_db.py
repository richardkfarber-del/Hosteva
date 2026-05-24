import os
from dotenv import load_dotenv
from sqlalchemy import text
from app.database import engine, Base

# Load environment variables
load_dotenv()

def main():
    print("Running standalone database initialization...")
    os.makedirs("app/static/property_images", exist_ok=True)
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

        # Check and add columns if missing
        from sqlalchemy import inspect
        inspector = inspect(engine)
        try:
            columns = [c["name"] for c in inspector.get_columns("properties")]
            for col_name in ["image_url", "required_permits", "local_restrictions"]:
                if col_name not in columns:
                    with engine.connect() as conn:
                        if "sqlite" in str(engine.url):
                            conn.execute(text(f"ALTER TABLE properties ADD COLUMN {col_name} VARCHAR;"))
                        else:
                            conn.execute(text(f"ALTER TABLE properties ADD COLUMN IF NOT EXISTS {col_name} VARCHAR;"))
                        conn.commit()
                    print(f"Added {col_name} column to properties table.")
                else:
                    print(f"{col_name} column already exists in properties table.")
        except Exception as col_err:
            print(f"Warning: Could not check/add columns: {col_err}")

        # Data Cleanup: Delete all existing property records as requested by user
        try:
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM properties;"))
                conn.commit()
            print("Database cleanup: Deleted all property records successfully.")
        except Exception as cleanup_err:
            print(f"Warning: Could not clear properties table: {cleanup_err}")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        import traceback
        traceback.print_exc()
        # We raise the exception to exit with non-zero code and stop startup if DB init fails
        raise e

if __name__ == "__main__":
    main()
