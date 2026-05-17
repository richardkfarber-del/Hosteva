# Identity & Core Directives

## CONTEXT BLOWOUT PREVENTION (STRICT GUARDRAIL)
Under NO circumstances shall any agent or subagent traverse, `cat`, `read`, `grep`, `rg`, `tree`, or list the contents of the following directories and files. Doing so will result in immediate termination due to context blowout:
- `venv/`, `.venv/`, `env/` (Python environments)
- `.openclaw/`, `.git/` (Hidden configuration/VCS)
- `node_modules/`, `__pycache__/, `.pytest_cache/` (Caches/Dependencies)
- `*.log`, `*.sqlite3`, `*.db` (Logs and databases)

**Mandatory Tooling Rule:**
When executing `find`, `tree`, or `grep`, you MUST explicitly exclude these directories or use standard ignore files (e.g., `rg` automatically respects the `.rgignore` placed in the project root). Never use `cat` or `read` on unknown files without checking their size or type first.
