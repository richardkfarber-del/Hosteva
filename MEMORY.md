## Render Production Deployment Hard Rules (Do Not Regress)
1. **Never** initialize database schemas/extensions globally in `app/main.py`. It blocks Gunicorn worker port binding on Render. Use `app/scripts/init_db.py`.
2. **Never** hardcode `EXPOSE 8000` as the bind port. Render dynamically injects `$PORT`. Use `CMD gunicorn ... --bind 0.0.0.0:${PORT:-8000}`.
3. **Never** use `psycopg2`. `python:3.12-slim` cannot dynamically link it without massive C-compiler bloat. Use `psycopg[binary]` v3.
4. **Never** blindly accept Render's `DATABASE_URL`. It injects `postgresql://`, defaulting to legacy drivers. You must intercept and rewrite it to `postgresql+psycopg://`.

## The Triple Doctrine Architecture
1. **The Micro-Tasking Doctrine:** Local models (`qwen2.5-coder`, `mistral-nemo`) cannot handle orchestration. Give them ONE task.
2. **The Code Writer Delegation:** Local models must NOT use the `exec`/`write` tools. They output raw markdown/code blocks; the Orchestrator uses Cloud API to inject the files.
3. **The Dual-Pronged QA Doctrine:** "The API works" does not mean the UI works. QA requires both the automated `scripts/run_uat_regression.py` payload test AND a headless browser DOM snapshot validation. When parsing the DOM, QA must use `snapshotFormat: 'ai'` to prevent context blowouts.

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
- **Daemon Enforcement:** [DEPRECATED by Sprint 12 Temporal Mandate] The LangGraph Autopilot (`graph.py`) and background subprocess daemons are permanently forbidden. The system must strictly use Temporal.io and Inotify File Watchers.

### 3. The Official Sprint Closure Pipeline
Sprints CANNOT be closed until this exact sequence executes sequentially:
1. **Gate 3: Production Deployment** (Heimdall pushes to Render).
2. **Gate 4: Production UAT** (Cap tests in live prod + captures PNG snapshots).
3. **Validation Audit** (Coulson physically verifies QA completed all requirements).
4. **Sprint Marked DONE** (Coulson logs it in the ledger).
5. **Team Retrospective** (The execution agents—Iron Man, Wasp, Cap, Hulk—report on friction, tools lacking, and workflow efficiency).
6. **Executive Review (The Evolution Loop)**: The Executive board reviews the Team Retrospective. Wanda (Scarlet Witch) is explicitly mandated to perform a "Deep Write" by permanently appending successful Retrospective rules and friction resolutions directly into the `SKILL.md` and `SOUL.md` of the individual execution agents. This structural memory injection ensures the swarm does not regress on reboots. Only after this step is confirmed can the next sprint begin.
## 🚨 SPRINT 11 CATASTROPHE: THE AI HALLUCINATION PROTOCOLS
*(Burned in by the Executive Strike Team: Shuri, Kang, Coulson, Jarvis on 2026-04-14)*

### 1. The Single-Turn Completion Bias (Shuri's Diagnosis)
Local models (Qwen/Llama) naturally hallucinate tool executions to satisfy macro-prompts in a single turn. 
- **Rule:** Agents must be explicitly prompted: "Do NOT output JSON or text claiming you completed a physical action. You MUST physically invoke the tool (e.g., `browser`, `edit`) and await the system's output."

### 2. The Immutable Tollgate (Kang & Coulson's Checksum Protocol)
The Orchestrator and Ledger Auditor MUST NEVER trust a subagent's text output claiming a task is "DONE".
- **Rule:** Before routing to Gate 3 (Deploy) or Gate 4 (UAT), the system MUST mathematically verify physical reality.
- **Dead-Drop Requirement:** Subagents must provide `md5sum` file hashes, `ls -la` byte sizes, or raw `git diff` outputs. 
- **"Show Me, Don't Tell Me" Loop:** If physical file changes or screenshot artifacts (e.g., in `/marketing/snapshots`) do not exist on the hard drive, the system automatically rejects the completion and forces a retry.

### 3. Micro-Tasking & The Guard Node (Jarvis's Telemetry)
Local LLM attention mechanisms degrade when given multi-step plans and too many tools.
- **Tool Stripping:** Irrelevant tools must be dynamically stripped from the prompt. If a node only reads, it should not know `write` exists.
- **Action-Verification Guard Node:** Temporal Workflows must intercept subagent outputs. If the agent says "I fixed the file" but no tool execution metadata is registered in the state, the Guard Node intercepts, blocks the progression, and replies with a strict negative prompt forcing actual tool usage.

## 🌩️ SPRINT 12: TEMPORAL ORCHESTRATION MANDATE
*(Enforced by Executive Board: Sprint 12 Retrospective)*

### 1. Mandatory Swarm Orchestration Framework
- **Temporal.io & Inotify:** The 'Temporal.io' architecture and 'Inotify File Watcher' are permanently locked as the mandatory Swarm orchestration framework.
- **Deprecated Patterns:** Any future use of Python `while True` polling loops, background `subprocess` daemons, or manual `graph.py` shell scripts is permanently deprecated and strictly forbidden.
- **CLI Native Spawning:** When spawned programmatically by Temporal, the Swarm MUST ONLY use the native `openclaw agent --json` CLI command. No wrapper scripts or background daemon wrappers are permitted.

## Dynamic Model Routing Protocol (Sprint 13 Override)
- **Default Execution:** All execution agents (Iron Man, Wasp, Cap) must default to `google/gemini-3-pro-preview` (or equivalent frontier model) for coding, architectural refactoring, and UI/DOM parsing.
- **Local Fallback Restriction:** Local quantized inference (e.g., `qwen2.5-coder` on RTX 4070) is strictly restricted to simple, small tasks. 
- **The Tollgate:** The decision to downgrade a task to a local model must be explicitly determined and flagged during Backlog Refinement (Phase 1 / Hawkeye / Jarvis). If not explicitly flagged as "Local-Safe", the orchestrator MUST spawn the subagent using the Gemini model parameter.

## The API Handshake Protocol & State Lifecycle (Sprint 13 Override)
The Swarm operates on a strict, cryptographically enforced state machine via the FastAPI backend (`POST /state/update`). Agents MUST NOT rely solely on chat text to advance the pipeline.

**The 11 Official Ticket Statuses:**
1. **`BACKLOG`**: Ticket generated by Hawkeye.
2. **`REFINEMENT`**: Team (Cap, Vision, Iron Man, Wasp) actively reviews the ticket for technical feasibility.
3. **`FAILED_REFINEMENT`**: Ticket rejected by the team due to negative feedback or missing context; sent back to Hawkeye.
4. **`BUILDING`**: Execution Squad (Iron Man, Wasp, etc.) is writing code.
5. **`BLOCKED`**: Ticket halted due to an external dependency or because another ticket must be completed first.
6. **`AUDITING`**: Coulson verifying file hashes. *MANDATORY: The API payload must contain the `md5sum` hashes.*
7. **`TESTING`**: Captain America running headless QA. *MANDATORY: The API payload must contain the `/marketing/snapshots/` PNG path.*
8. **`REJECTED`**: Code failed Audit or QA; sent back to `BUILDING`.
9. **`PENDING_APPROVAL`**: Swarm paused; strictly awaiting Director (Richard Farber) authorization.
10. **`DEPLOYING`**: Heimdall actively pushing to Render production.
11. **`DONE`**: Deployed, Retro complete, and Wanda has executed the Deep Write.

**Enforcement:**
An agent cannot begin work on a phase unless the API `GET /state/status/{ticket_id}` mathematically confirms the ticket is in the correct prerequisite state.

### API Handshake Protocol: Technical Implementation
When an agent completes a task, they MUST use the `exec` tool to fire a curl request to update the state machine. They must NEVER yield without doing this.
**Format:**
```bash
curl -X POST http://localhost:8000/state/update \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": "BUG-003", "status": "PENDING_APPROVAL", "agent_name": "Wasp", "payload": {"md5sum": "your_hash_here"}}'
```
