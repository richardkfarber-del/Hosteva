import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Intercept Render's database URL environment variables and rewrite it to the postgresql+psycopg:// schema.
# Prioritize INTERNAL_DATABASE_URL over DATABASE_URL.
SQLALCHEMY_DATABASE_URL = os.environ.get("INTERNAL_DATABASE_URL") or os.environ.get("DATABASE_URL")

# If no database URL is set, default to a persistent SQLite database
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "sqlite:///hosteva.db"

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif SQLALCHEMY_DATABASE_URL.startswith("postgresql://") and not SQLALCHEMY_DATABASE_URL.startswith("postgresql+psycopg://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    if ":memory:" in SQLALCHEMY_DATABASE_URL:
        SQLALCHEMY_DATABASE_URL = "sqlite:///hosteva.db"

DATABASE_URL = SQLALCHEMY_DATABASE_URL # alias for backwards compatibility

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

from sqlalchemy.event import listens_for
@listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


