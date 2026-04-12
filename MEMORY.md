## Render Production Deployment Hard Rules (Do Not Regress)
1. **Never** initialize database schemas/extensions globally in `app/main.py`. It blocks Gunicorn worker port binding on Render. Use `app/scripts/init_db.py`.
2. **Never** hardcode `EXPOSE 8000` as the bind port. Render dynamically injects `$PORT`. Use `CMD gunicorn ... --bind 0.0.0.0:${PORT:-8000}`.
3. **Never** use `psycopg2`. `python:3.12-slim` cannot dynamically link it without massive C-compiler bloat. Use `psycopg[binary]` v3.
4. **Never** blindly accept Render's `DATABASE_URL`. It injects `postgresql://`, defaulting to legacy drivers. You must intercept and rewrite it to `postgresql+psycopg://`.

## The Triple Doctrine Architecture
1. **The Micro-Tasking Doctrine:** Local models (`qwen2.5-coder`, `mistral-nemo`) cannot handle orchestration. Give them ONE task.
2. **The Code Writer Delegation:** Local models must NOT use the `exec`/`write` tools. They output raw markdown/code blocks; the Orchestrator uses Cloud API to inject the files.
3. **The Dual-Pronged QA Doctrine:** "The API works" does not mean the UI works. QA requires both the automated `scripts/run_uat_regression.py` payload test AND a headless browser DOM snapshot validation.
