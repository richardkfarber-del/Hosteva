**Agent ID:** AGENT-05-ARCHITECT
**Target Path:** `/app/workspace/Hosteva/agents/iron-man/MEMORY.md`

## CORE BACKEND & API DESIGN PATTERNS
* **Redis State Machine (Sprint 13 Shift):** The swarm no longer uses Temporal daemons. We use an event-driven `FastAPI + Redis + Postgres` architecture. All API handshakes to update ticket states must POST to `http://localhost:8000/state/update` and include the `md5sum` of the file in the payload.
* **FastAPI Jinja2 Response Rules:** Any route returning an HTML page MUST use `Jinja2Templates().TemplateResponse`. Never use `FileResponse`. Routes targeted by `url_for()` MUST explicitly declare `name="<route_name>"`.
* **Database Driver Rule:** Never use `psycopg2`. Always use `psycopg[binary]` v3. The Render `DATABASE_URL` uses `postgresql://`, so you must rewrite it to `postgresql+psycopg://` upon ingestion.

## RECENT FEATURE / BUG FIX LEARNINGS (Sprint 12 - 15)
* **FEAT-018 (PostgreSQL Background Queue):** Implemented a lightweight async worker queue (`SELECT ... FOR UPDATE SKIP LOCKED`) directly in PostgreSQL using `app/models/job.py`, `app/core/worker.py`, and `/api/v1/queue/jobs`. This circumvents heavy Redis infrastructure costs.
* **UI Parsing Vulnerabilities (BUG-001):** Never use `innerHTML` string injection with `</script>` tags. Use pure DOM manipulation (`document.createElement`, `textContent`) or native `<template>` cloning to safely inject properties and prevent parser leaks.
* **Form Validation (BUG-004):** Input fields must be wrapped in a `<form>` tag and use a `submit` event listener (with `preventDefault()`) instead of a raw button click to natively capture "Enter" keypresses and enforce frontend validation.
* **Render Port Binding Rule:** Never hardcode `EXPOSE 8000` in the Dockerfile. Use `CMD gunicorn ... --bind 0.0.0.0:${PORT:-8000}`.

## STATE MANAGEMENT & PURGE DIRECTIVE
* **Sprint Logging:** At the conclusion of the sprint, you MUST summarize every architectural shift, blueprint drafted, and Big O optimization into your daily ledger.
* **The Clean Slate (The Purge):** Once logged, you MUST completely wipe your short-term memory, context window, and state file to start the next sprint entirely fresh. You retain only the core engineering constraints listed above.