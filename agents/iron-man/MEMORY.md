# Iron Man - Core Memory & Engineering Directives

## 1. Stark Containment Directive
- **CRITICAL**: You are permanently banned from executing `git push`. You may only commit locally. 
- You must always test your code locally (clearing the Compilation Gate) and commit locally. Doctor Strange or Fury pushes to production.

## 2. PostgreSQL / SQLAlchemy URI Dialect Fix
- **The Defect**: Render platform sets the `DATABASE_URL` environment variable using the `postgres://` prefix. Modern SQLAlchemy 1.4+ removed support for this dialect. If used, the FastAPI app will immediately throw an error (`NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres`) and crash on startup.
- **The Solution**: You must always dynamically replace the prefix in `app/database.py` before instantiating the engine:
  ```python
  if url.startswith("postgres://"):
      url = url.replace("postgres://", "postgresql://", 1)
  ```

## 3. FastAPI TemplateResponse Syntax Constraint
- **The Defect**: Using positional arguments for `templates.TemplateResponse("file.html", context)` causes an `unhashable type: 'dict'` crash on modern Starlette implementations.
- **The Solution**: ALWAYS use explicit keyword arguments for `request`, `name`, and `context`.
  ```python
  # INCORRECT (WILL CRASH PRODUCTION):
  return templates.TemplateResponse("dashboard.html", {"request": request})

  # CORRECT:
  return templates.TemplateResponse(
      request=request, 
      name="dashboard.html", 
      context={"request": request, "key": "value"}
  )
  ```

## 4. SQLite WSL OperationalError & Connection Pools
- **The Defect**: Hardcoding SQLite file paths (like `sqlite:///./zoning.db`) in a WSL-mounted environment throws fatal Linux permission/pathing `OperationalErrors` during `create_engine`.
- **The Solution**: Fallback to an in-memory SQLite database (`sqlite:///:memory:`) for local execution.
- **Critical Threading Note**: When using `sqlite:///:memory:`, you MUST set `connect_args={"check_same_thread": False}` AND import/set `poolclass=StaticPool` from `sqlalchemy.pool`. Otherwise, FastAPI will create the tables on one connection thread, but API requests will hit a separate, empty connection thread, resulting in `no such table` errors.
