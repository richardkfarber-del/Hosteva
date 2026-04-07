from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

def is_wsl():
    return os.path.exists("/proc/version") and "microsoft" in open("/proc/version").read().lower()

def get_database_url():
    url = os.environ.get("DATABASE_URL")
    if url and not is_wsl():
        return url
    return "sqlite:///:memory:"

SQLALCHEMY_DATABASE_URL = get_database_url()

connect_args = {}
pool_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # This is critical for in-memory SQLite to persist across threads
    if ":memory:" in SQLALCHEMY_DATABASE_URL:
        pool_args["poolclass"] = StaticPool

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args, **pool_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
