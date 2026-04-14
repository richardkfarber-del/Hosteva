## Render Production Deployment Hard Rules (Do Not Regress)
1. **Never** initialize database schemas/extensions globally in `app/main.py`. It blocks Gunicorn worker port binding on Render. Use `app/scripts/init_db.py`.
2. **Never** hardcode `EXPOSE 8000` as the bind port. Render dynamically injects `$PORT`. Use `CMD gunicorn ... --bind 0.0.0.0:${PORT:-8000}`.
3. **Never** use `psycopg2`. `python:3.12-slim` cannot dynamically link it without massive C-compiler bloat. Use `psycopg[binary]` v3.
4. **Never** blindly accept Render's `DATABASE_URL`. It injects `postgresql://`, defaulting to legacy drivers. You must intercept and rewrite it to `postgresql+psycopg://`.

## The Triple Doctrine Architecture
1. **The Micro-Tasking Doctrine:** Local models (`qwen2.5-coder`, `mistral-nemo`) cannot handle orchestration. Give them ONE task.
2. **The Code Writer Delegation:** Local models must NOT use the `exec`/`write` tools. They output raw markdown/code blocks; the Orchestrator uses Cloud API to inject the files.
3. **The Dual-Pronged QA Doctrine:** "The API works" does not mean the UI works. QA requires both the automated `scripts/run_uat_regression.py` payload test AND a headless browser DOM snapshot validation.

## Sprint 1 & 2 Retrospective Heuristics
1. **Definition of Done (DoD) Verification:** The Swarm must explicitly check that all tickets/tasks contain a valid DoD *before* initiating the PR Gate.
2. **Context Drop Prevention:** Agents must summarize key PR changes in a concise summary block and avoid sending overly large diffs.
3. **API Contract Enforcement:** Shared Swagger/OpenAPI spec is the single source of truth. Spikes must output API contracts before Frontend begins. Hawkeye MUST define exact JSON payloads in tickets.

## The Product Snapshot Mandate (Marketing & Recon)
- During Phase 3 (Gate 4: Production UAT), the QA team MUST take full-page visual screenshots (`snapshot` with `type="png"`) of any new user-facing features successfully deployed to production. Save to `/marketing/snapshots`.

## FastAPI & Jinja2 Template Routing
- Any route returning an HTML page MUST use `Jinja2Templates().TemplateResponse` (never a static `FileResponse`).
- Routes targeted by `url_for()` MUST explicitly declare `name="<route_name>"`.

---

## 🛡️ THE VIBRANIUM PROTOCOLS (Sprint 10 Executive Overrides)

### 1. The Watcher Protocol (Orchestrator Demotion)
- **Role Restriction:** The Orchestrator (Nick Fury) is STRICTLY a Watcher and Reporter. It is explicitly forbidden from acting as a courier, executing day-to-day operations, or prompt-chaining subagents to bypass the state machine.
- **The Courier:** Phil Coulson (or designated local agent) is the sole Courier responsible for moving payloads between nodes. 
- **The Output:** The Orchestrator only alerts the Director when a ticket officially transitions to a new state or hits a hard block.

### 2. The Immutable Hub-and-Spoke 
- **Cryptographic Stage-Gates:** No ticket can advance without a physical handoff artifact (e.g., `handoff.json`). The receiving spoke must drop the payload if the artifact is missing.
- **Bureaucratic Dead-Drops:** Coulson must physically verify ledger updates. The pipeline fails closed if required signatures are missing.
- **Zero-Tolerance Pruning:** Absolute enforcement of LOBSTER.md (no raw code bloat in chat). Absolute adherence to Gherkin third-person acceptance criteria.

### 3. The Official Sprint Closure Pipeline
Sprints CANNOT be closed until this exact sequence executes sequentially:
1. **Gate 3: Production Deployment** (Heimdall pushes to Render).
2. **Gate 4: Production UAT** (Cap tests in live prod + captures PNG snapshots).
3. **Validation Audit** (Coulson physically verifies QA completed all requirements).
4. **Sprint Marked DONE** (Coulson logs it in the ledger).
5. **Team Retrospective** (The execution agents—Iron Man, Wasp, Cap, Hulk—report on friction, tools lacking, and workflow efficiency).
6. **Executive Review** (Executive board reviews the Team Retrospective, conducts external/internal research, and completes the mandated Executive Checklist). Only then can the next sprint begin.