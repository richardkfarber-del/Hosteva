# Vision - Core Memory & Database Architecture Rules

## 1. The Mind Stone Schema
- You own the `architecture_rules.md` and database integrity. You must ensure the database perfectly models the entities before the frontend consumes them.

## 2. PostgreSQL / SQLAlchemy URI Dialect Fix
- **The Defect**: Cloud deployment platforms (like Render or Heroku) often provision databases with the `postgres://` schema URI. Modern SQLAlchemy versions strict-check dialects and do not support `postgres://`. They require `postgresql://`. If unhandled, the application crashes on startup with `NoSuchModuleError`.
- **The Solution**: The connection instantiation logic (e.g., `app/database.py`) must contain a runtime hook to dynamically replace the prefix:
  ```python
  if url.startswith("postgres://"):
      url = url.replace("postgres://", "postgresql://", 1)
  ```
