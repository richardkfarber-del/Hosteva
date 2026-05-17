import os
import sys

os.environ["DATABASE_URL"] = "postgres://admin:pass@db.render.com/prod_db"

from app.database import SQLALCHEMY_DATABASE_URL
from app.core.config import Settings

settings = Settings()

try:
    assert SQLALCHEMY_DATABASE_URL.startswith("postgresql+psycopg://"), f"database.py failed: {SQLALCHEMY_DATABASE_URL}"
    assert settings.sqlalchemy_database_url.startswith("postgresql+psycopg://"), f"config.py failed: {settings.sqlalchemy_database_url}"
    print("SUCCESS: DATABASE_URL successfully rewritten to postgresql+psycopg:// schema for Render compatibility.")
except AssertionError as e:
    print(f"FAIL: {e}")
    sys.exit(1)
