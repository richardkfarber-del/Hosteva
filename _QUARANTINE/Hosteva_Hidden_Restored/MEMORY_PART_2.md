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

## 🧪 WANDA'S DEEP WRITE: TEST-DRIVEN DEVELOPMENT (TDD) MANDATE
*(Authorized by Secretary Farber: 2026-04-16)*

1. **The Pytest Prerequisite (Execution Squad):**
   * Iron Man, Vision, Wasp, and any other execution agents are strictly forbidden from pushing code to `AUDITING` without generating an accompanying automated test suite (e.g., `pytest` for backend, Jest/integration tests for frontend). 
   * The test files MUST be committed to the repository alongside the application code in Phase 2.

2. **The Automated QA Crucible (Captain America):**
   * Captain America's bandwidth is reserved for high-level UAT and architectural validation. During Phase 4 (The Crucible), Cap MUST execute the automated test suites generated by the Execution Squad via the `exec` tool (e.g., `pytest tests/`). 
   * If the tests fail, or if test coverage is missing, Captain America will instantly REJECT the ticket and route it back to Phase 2. He will no longer manually hunt for basic syntax errors or endpoint regressions.

## 🔮 WANDA'S DEEP WRITE: SPRINT 22 ARCHITECTURAL LOCKS
*(Authorized by Secretary Farber: Sprint 22)*

1. **Clean Architecture Strictness (Domain Isolation):**
   * Swarm Workers (infrastructure) must NEVER hardcode domain state transitions (like `FAILED_ESCALATED` or 3-strike rules). 
   * All state routing and escalation logic must be handled natively in the FastAPI domain layer (`app/api/routes/swarm.py`).

2. **Hardware Lock Flush (RTX 4070 Protection):**
   * Any ticket that hits a 3-strike escalation limit MUST trigger a physical VRAM flush (`pkill -9 -f openclaw-gateway`) via the FastAPI backend to protect the host's RTX 4070 hardware.

3. **LangGraph Purge (Zero Ghost Processes):**
   * LangGraph is permanently banned. Any legacy scripts like `test_graph.py` or `src/swarm/graph` that attempt to mock the CLI will spawn ghost processes and are strictly forbidden.

4. **Prime Directive Enforcement (Orchestrator Containment):**
   * The Orchestrator (Nick Fury) is strictly forbidden from manually writing Python patches or bypassing the subagent pipeline.

## 🔮 WANDA'S DEEP WRITE: V3.0 13-STEP PIPELINE OVERHAUL
*(Authorized by Secretary Farber: Post-SPIKE-008)*

### 1. Shift-Left Threat Council & Domain Bypass Protocol
- **Refinement (Step 2):** Must dynamically spawn the FULL Vanguard PLUS the Threat Council (Black Panther, She-Hulk, Falcon, Kang, Iron Man, Vision).
- **Mandate:** Security and Legal MUST review and approve constraints before any code is built.
- **Domain Bypass:** Agents outside their domain must explicitly PASS. Captain America retains the Definition of Ready veto.

### 2. Post-Deployment Lifecycle
- **Step 7 (DEPLOYING):** Heimdall pushes to Render.
- **Step 8 (PROD_DEPLOYED):** Deployment successful.
- **Step 9 (POST_PROD_QA):** QA team runs headless tests natively against the live production environment.
- **Step 10 (RETROSPECTIVE):** All sprint agents submit feedback to a master report.
- **Step 11 (EXECUTIVE_REVIEW):** **[HARD HALT]** Awaiting Secretary and Director review of the Retro report.
- **Step 12 (DEEP_WRITE_DONE):** Wanda is triggered to append permanent memory *only* after live Secretary feedback is provided. Ticket officially closed.

### 3. SPIKE_REVIEW Hard Halt
- If the ticket type is a `SPIKE`, it bypasses `PENDING_APPROVAL` after `TESTING` (or `REFINEMENT` if no code). It routes directly to `SPIKE_REVIEW` **[HARD HALT]**.
- **Secretary Approves** -> `DONE`.
- **Secretary Rejects** -> Routes back to `REFINEMENT` (Strike counter increments).

### 4. Circular Loop Prevention (The 3-Strike Rule)
- Active routing replaces dead-end states (`FAILED_REFINEMENT` and `REJECTED` now actively ping Hawkeye or Execution Squad & the Secretary).
- **The 3-Strike Rule:** A global state counter is enforced. If a ticket is rejected 3 times, it routes to `FAILED_ESCALATED` **[HARD HALT]**, requiring manual Secretary intervention to prevent endless loops.
