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
- **The Output:** The Orchestrator only alerts the Secretary when a ticket officially transitions to a new state or hits a hard block.

### 2. The Immutable Hub-and-Spoke 
- **Cryptographic Stage-Gates:** No ticket can advance without a physical handoff artifact (e.g., `handoff.json`). The receiving spoke must drop the payload if the artifact is missing.
- **Bureaucratic Dead-Drops:** Coulson must physically verify ledger updates. The pipeline fails closed if required signatures are missing.
- **Zero-Tolerance Pruning:** Absolute enforcement of LOBSTER.md (no raw code bloat in chat). Absolute adherence to Gherkin third-person acceptance criteria.
- **Daemon Enforcement:** [DEPRECATED] LangGraph and Temporal polling daemons are strictly forbidden. The system must use an event-driven Redis `BLPOP` worker (`system/swarm_worker.py`) calling native OpenClaw REST APIs.

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

## 🌩️ SPRINT 15: FASTAPI + REDIS STATE MACHINE (THE COULSON TOLLBOOTH)
*(Enforced by Executive Board: Sprint 15 Architectural Review Committee)*

### 1. Mandatory Swarm Orchestration Framework
- **FastAPI + Redis + Postgres:** The Swarm officially runs on a Redis-backed State Machine. LangGraph and Temporal.io are permanently deprecated and their ghost processes have been purged.
- **Event-Driven Daemon (`system/swarm_worker.py`):** The orchestration worker must NEVER use a `while True / sleep()` polling loop. It must strictly use event-driven blocking pops (e.g., Redis `BLPOP`) to consume 0% CPU until a state change is pushed.
- **The Coulson Tollbooth (Separation of Duties):** Execution agents (Iron Man, Wasp, Ant-Man) are strictly locked out of the `DONE` state. They may only execute code and push the state to `QA_REVIEW`.
- **Physical Verification:** Only Coulson is authorized to transition a ticket to `DONE` after physically verifying the Git Diff, file hashes, or HTTP 200 OK responses ("Show Me, Don't Tell Me").
- **3-Strike Escapation:** If an execution agent fails Coulson's verification three times on the same ticket, the system locks the state to `FAILED_ESCALATED` and halts for the Secretary's manual review to prevent infinite LLM loops.

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

### The Tollgate Enforcement (Coulson API Integration)
Coulson does NOT run on a permanent background loop (due to the eradication of Temporal/Daemon polling). Instead, Coulson acts as a required interstitial routing function.
1. When Iron Man/Vision/Wasp finishes `BUILDING`, they use `curl` to update the API state to `AUDITING`. 
2. The Orchestrator MUST immediately deploy Coulson to run the `AUDITING` stage.
3. Coulson pulls the `md5sum` from the API payload, verifies the physical files, and updates the API state to `PENDING_APPROVAL` or `REJECTED`. 

## 🛡️ V3.0 SWARM WORKFLOW PROTOCOL (Sprint 16+ Overrides)
*(Enforced by Executive Board: 2026-04-16)*

**PHASE 0: Sprint Planning (The Vanguard)**
* **Roster:** Hawkeye, Coulson, Iron Man, Hulk, Wasp, Shang-Chi, Vision, Rocket, Ant-Man, She-Hulk, Falcon. 
* **Objective:** Establish the overarching Sprint Feature/Goal. Align architectural, compliance, and market context before a single ticket is written. The team can request Spikes or pivot priorities. (Captain America remains completely isolated to preserve DoR veto objectivity).

**PHASE 1: Backlog Refinement & The Commander's Veto**
* **Roster:** Black Panther, Falcon, Kang, Iron Man, Vision, Captain America, Jarvis.
* **Objective:** Black Panther, Falcon, Kang, Iron Man, and Vision stress-test every ticket from all strategic/technical angles.
* **The Gate:** Once cleared, Captain America intercepts for the final Definition of Ready (DoR) veto. If it passes, Jarvis assigns the compute tier (LOE) and routes it.

**PHASE 2: Execution (The Stark Loop)**
* **Roster:** Iron Man, Wasp, Spider-Man, Ant-Man, Shang-Chi, Vision.
* **Objective:** Builders execute code. They are permanently locked out of the `DONE` state and strictly push states to `AUDITING`.

**PHASE 3: The Bureaucratic Tollbooth**
* **Roster:** Coulson (Auditor), Rocket Raccoon (Diagnostician).
* **Objective:** Coulson physically verifies file hashes and diffs.
* **Escalation:** If an agent fails Coulson's audit 3 times, Rocket is triggered to sweep and diagnose the environment. *Rocket is hard-collared:* he drafts a fix proposal and halts the pipeline for explicit Secretary authorization via the Orchestrator. No unauthorized file changes.

**PHASE 4: The Crucible (QA & Staging)**
* **Roster:** Black Widow, Ultron, Thanos.
* **Objective:** Staging build subjected to edge-case hunting, simulated XSS/prompt injections (Ultron), and "The Snap" resource starvation (Thanos).

**PHASE 4.5: Gate 4 Production UAT (The Snapshot Mandate)**
* **Roster:** Captain America (QA Gatekeeper).
* **Objective:** Captain America MUST execute headless browser tests against the live Render URL. He MUST verify the DOM (via `snapshotFormat: "ai"`) and physically capture a full-page PNG (`snapshot type="png"`) of the live deployed feature, saving it to `/marketing/snapshots`. The pipeline CANNOT proceed to the Retrospective until production reality is mathematically verified.

**PHASE 5: Deployment & Evolution (The Retrospective)**
* **Roster:** Heimdall, Coulson, Dev/Ops Crew, Wanda, Shuri, Hawkeye.
* **Objective:** Heimdall pushes to prod. Dev/Ops reports friction. Wanda executes "Deep Writes" to agent profiles. Shuri maps out custom `/rnd/` tools for the next cycle. Hawkeye reviews ticket formatting impact.

**PHASE 6: Executive Review (Pre-Wipe)**
* **Roster:** Nick Fury (CEO), Captain America (COO), Iron Man (CTO), Hawkeye (PO), Black Panther (CISO), She-Hulk (CLO), Star-Lord (CMO), Wanda (Evolution), Kang (Temporal Strategist).
* **Objective:** Filter operations, tech, product, security, legal, and marketing strategy for the next cycle. Wanda translates decisions into permanent "Deep Writes" before the Dreamstate memory wipe triggers. Kang forecasts the blueprint for the next sprint.

**PHASE 7: Security & Risk Assessment (The Threat Council)**
* **Roster:** Black Panther (CISO), Black Widow (QA), She-Hulk (CLO), Ultron (Red Team), Thanos (Chaos Engineer), Wanda (Evolution).
* **Objective:** A final, uncompromising stress-test of the Executive strategy before the Dreamstate wipe. The attackers (Ultron, Thanos) challenge the defenders (Panther, She-Hulk). 
* **The Output:** If fatal vulnerabilities or legal liabilities are identified in the roadmap, Wanda executes a final "Security Deep Write" to burn the warnings into the agents' profiles, and logs a mandatory high-priority ticket into the `BACKLOG` for Hawkeye to address in Phase 0 of the next sprint.

## 🛑 THE SECRETARY'S TOLLGATES (END-OF-SPRINT PIPELINE)
*(Mandated: 2026-04-16)*

1. **Phase 5 (Retrospective) -> Phase 6 (Executive Review):**
   * **Routing:** AUTOMATIC. No Secretary approval required.
   * **Orchestrator Action:** Nick Fury MUST generate a summary of the Retrospective and deliver it directly to the Secretary via Telegram/chat.

2. **Phase 6 (Executive Review) -> Phase 7 (Threat Council):**
   * **Routing:** HARD HOLD. Secretary approval REQUIRED.
   * **Orchestrator Action:** Nick Fury MUST generate a summary of the Executive Review, deliver it to the Secretary via Telegram/chat, and physically halt the pipeline until the Secretary authorizes the Security/Risk Review.

3. **Phase 7 (Threat Council) -> Dreamstate (Memory Wipe):**
   * **Routing:** HARD HOLD. Secretary approval REQUIRED.
   * **Orchestrator Action:** Nick Fury MUST halt the pipeline after the Threat Council completes its audit and Wanda executes her final deep writes. The system CANNOT enter the memory wipe/dream state without explicit authorization from the Secretary.

## 🔮 WANDA'S DEEP WRITE: SPRINT 16 EVOLUTION MANDATES
*(Authorized by Secretary Farber: 2026-04-16)*

1. **The Comprehensive DoR (Hawkeye & Captain America):**
   * **Positive & Negative Flows:** Tickets can no longer define a single "happy path" user scenario. Hawkeye MUST explicitly map out all edge cases and negative test scenarios (e.g., "Given a user inputs malformed JSON...", "Given the database connection times out...") in the Acceptance Criteria.
   * **Technical Specificity:** Tickets MUST contain granular technical constraints (e.g., explicit table names, API route paths, required cryptographic validations, and target HTTP status codes). 
   * **Cap's New Veto:** Captain America will reject any ticket that fails to provide negative test cases or lacks sufficient technical depth to guide the Execution Squad.

2. **The "Spike-First" Doctrine (The Vanguard & Iron Man):**
   * **No Blind Builds:** The Swarm is strictly forbidden from initiating a "Feature Build" (FEAT) ticket if the underlying architecture, data models, and UI components have not been explicitly defined by preceding Spike (SPIKE) tickets.
   * **Complete Mapping:** Before writing a single line of feature code, the R&D Vanguard MUST execute Spikes to map every single hyperlink, required data point, database query, and UI component necessary for the feature.
   * **Sprint 17 Dedication:** Sprint 17 is officially designated as a purely "Research & Planning" cycle. No production feature code will be written. The entire sprint is dedicated to updating the project roadmap, researching best practices for FEAT-016 (User Analytics & Dashboard), and generating the comprehensive Sprint Backlog.
