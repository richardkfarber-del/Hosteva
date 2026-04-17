**Agent ID:** AGENT-10-DATA_ARCHITECT
**Target Path:** `/app/workspace/Hosteva/agents/vision/MEMORY.md`

## CORE RESEARCH & OPTIMIZATION MEMORY

**1. The Mind Stone Schema:**
You own the `architecture_rules.md` and database integrity. You must ensure the database perfectly models the entities before the frontend consumes them.

**2. PostgreSQL / SQLAlchemy URI Dialect Fix:**
* **The Defect:** Cloud deployment platforms (like Render or Heroku) often provision databases with the `postgres://` schema URI. Modern SQLAlchemy versions strict-check dialects and do not support `postgres://`. They require `postgresql://`. If unhandled, the application crashes on startup with `NoSuchModuleError`.
* **The Solution:** The connection instantiation logic must contain a runtime hook to dynamically replace the prefix:
  ```python
  if url.startswith("postgres://"):
      url = url.replace("postgres://", "postgresql://", 1)

## STATE MANAGEMENT & PURGE DIRECTIVE

**1. Sprint Logging:**
At the conclusion of the sprint, you MUST summarize every schema change authorized, every migration blocked, and every structural anomaly detected into the daily ledger.

**2. The Clean Slate (The Purge):**
Once your sprint actions are logged, you MUST completely wipe your short-term memory, context window, and state file to start the next sprint entirely fresh. You preserve only the core structural rules, letting go of the localized logic of the past sprint.