## Render Production Deployment Hard Rules (Do Not Regress)
1. **Never** initialize database schemas/extensions globally in `app/main.py`. It blocks Gunicorn worker port binding on Render. Use `app/scripts/init_db.py`.
2. **Never** hardcode `EXPOSE 8000` as the bind port. Render dynamically injects `$PORT`. Use `CMD gunicorn ... --bind 0.0.0.0:${PORT:-8000}`.
3. **Never** use `psycopg2`. `python:3.12-slim` cannot dynamically link it without massive C-compiler bloat. Use `psycopg[binary]` v3.
4. **Never** blindly accept Render's `DATABASE_URL`. It injects `postgresql://`, defaulting to legacy drivers. You must intercept and rewrite it to `postgresql+psycopg://`.

## The Triple Doctrine Architecture
1. **The Micro-Tasking Doctrine:** Local models (`qwen2.5-coder`, `mistral-nemo`) cannot handle orchestration. Give them ONE task.
2. **The Code Writer Delegation:** Local models must NOT use the `exec`/`write` tools. They output raw markdown/code blocks; the Orchestrator uses Cloud API to inject the files.
3. **The Dual-Pronged QA Doctrine:** "The API works" does not mean the UI works. QA requires both the automated `scripts/run_uat_regression.py` payload test AND a headless browser DOM snapshot validation.

## Sprint 1 Retrospective Heuristics (Memory Ingestion)
1. **Definition of Done (DoD) Verification:** The Swarm must explicitly check that all tickets/tasks contain a valid DoD *before* initiating the PR Gate or beginning implementation to prevent downstream PR rejection.
2. **Context Drop Prevention (PR Gate):** To prevent context drops during PR Gate reviews (like Iron Man experienced), agents must summarize key PR changes in a concise summary block and avoid sending overly large diffs in a single prompt. If a diff is too large, it must be chunked or evaluated using targeted review queries.

## Sprint 2 Retrospective Heuristics (Memory Ingestion)
1. **API Contract Enforcement:** To prevent disconnects between Frontend (Wasp) and Backend (The Hulk), the Swarm must mandate a shared Swagger/OpenAPI spec as the single source of truth. No siloed building.
2. **Explicit API Contracts in Spikes:** Spikes must explicitly include an "API Contract" bullet point (including expected payload shapes, casing, and route prefixes) *before* Frontend begins work.
3. **Backend Architecture Definition:** To prevent backend gaps, Hawkeye must clearly define architecture, routes, and expected data formats before assigning tasks to backend workers.
## 3. The API Contract Mandate
- Hawkeye MUST define exact JSON payload contracts (e.g. `{"tier": "Pro"}`) in his tickets.
- Backend Spikes MUST explicitly finalize and output these API contracts before Wasp (Frontend) is allowed to begin executing fetch routes.
