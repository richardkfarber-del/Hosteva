import os
os.environ['DATABASE_URL'] = 'postgres://user:pass@host:5432/db'
from app.database import SQLALCHEMY_DATABASE_URL
print(f"Rewritten URL: {SQLALCHEMY_DATABASE_URL}")
