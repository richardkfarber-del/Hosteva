# Hosteva Swarm: The Golden Pipeline

This document defines the absolute, unalterable process for all code generation, testing, and deployment. This must be referenced and enforced across all restarts and days.

## PHASE 1: BACKLOG REFINEMENT (THE CRUCIBLE)
Objective: Ensure absolute clarity, strict formatting, and architectural consensus before a ticket reaches a sprint.

### 1. The Draft (Hawkeye)
Hawkeye drafts the ticket in an isolated `.md` file, strictly adhering to formatting:
- **User Stories:** 3rd-person Gherkin syntax only (e.g., "Given a user is..."). Never first-person.
- **Tech & Spike Tickets:** Strict bulleted list Acceptance Criteria (AC). No Gherkin.
- **Bug Tickets:** "Expected Behavior" single sentence or bullet list. No Gherkin.

### 2. Coulson's Gate
Hawkeye passes the file path to Coulson. Coulson audits the formatting.
- If Hawkeye used 1st-person Gherkin, Coulson rejects it.
- If perfect, Coulson logs the draft in `daily_ledger.md` and opens the Swarm Review.

### 3. The Swarm Review (Via File Pointers)
Coulson routes the file path to Vision (Architecture), Wasp/Stark (Execution), Black Widow (QA), and Captain America (Agile Lead).

### 4. The Lock
Every reviewing agent must append their "Approved" stamp or actionable feedback directly into the ticket file.
- If Vision flags an architectural anti-pattern, the file is sent back to Hawkeye (via Coulson) for a rewrite.
- Once all approve, Captain America seals the ticket and Coulson logs the "Ready" state in `PROJECT_BOARD.md`.

## PHASE 2: SPRINT PLANNING (THE WAR ROOM)
Objective: Establish consensus, identify blockers, lock the scope, and log the state.

### 1. The Proposal (Fury)
Fury reads the locked backlog and presents the proposed sprint payload (via file paths) to the active Swarm.

### 2. Consensus & Capacity Check
- **JARVIS** models the compute/token cost (shifting routine tasks to local Gemma where possible).
- **Winter Soldier** checks if legacy characterization tests are needed.
- All executing agents review the target file paths against their capabilities.

### 3. Conflict Resolution
- Any negative feedback triggers an immediate revision.
- If the Swarm cannot autonomously resolve a dependency, it triggers a Hard Stop and Fury escalates to the Secretary.

### 4. The Lock (Captain America & Coulson)
- Captain America confirms feasibility.
- Coulson logs the official sprint manifest and start state in the ledger.
- No ad-hoc scope changes are permitted without restarting this phase.

## PHASE 3: EXECUTION & MULTI-STAGE QA (THE GAUNTLET)
Objective: Write the code and prove it works at three distinct layers of integration using pointer-handoffs.

### 1. Execution Loop
The Swarm is orchestrated by a persistent, event-driven Redis daemon (`system/swarm_worker.py`).
1. **The Jarvis Tollgate (LOE & Compute Arbiter):** When the worker detects a `PENDING` ticket, it first routes it to Jarvis. Jarvis evaluates the Level of Effort (LOE). If routine/easy, Jarvis downgrades the team to local hardware (`qwen2.5-coder` on RTX 4070). If complex, Jarvis upgrades the team to Gemini 3 Pro.
2. **The Assignment:** The worker then assigns the ticket and the designated compute tier to an Execution Agent (e.g., Iron Man, Wasp, Ant-Man, Shang-Chi). 
3. **The Output:** The Execution Agent writes the code. They are permanently locked out of the `DONE` state and cannot self-certify completion.
4. **The Yield:** The Agent yields their terminal output (a summary of changes, file paths, hashes). The daemon intercepts this yield and automatically transitions the ticket to `QA_REVIEW`.

### 2. Gate 1: Local Feature QA (The Coulson Tollbooth)
- **The Tollbooth:** The daemon routes all `QA_REVIEW` tickets directly to Coulson.
- **Physical Verification:** Coulson must physically verify the Execution Agent's claims using `md5sum`, `pytest`, or parsing DOM changes. 
- **The Escalate Loop:** If Coulson rejects the work, he kicks it back to `PENDING` with his failure logs. If he rejects it 3 times, the ticket locks to `FAILED_ESCALATED` and halts for Director review.
- **The PASS:** If Coulson replies `VERIFIED`, the daemon formally triggers the API to mark the ticket `DONE`.
- **Parallel Sweeps:** 
  - **Shang-Chi** intercepts code immediately for typing/linting.
  - **Black Widow** silently sweeps the isolated branch files for vulnerabilities.
  - **Jarvis** acts as the Guard Node, verifying tool execution metadata against text output.

### 3. Gate 2: Local Integration QA
- **Winter Soldier** (Chaos Engineering) load-tests the staging build and stress-tests APIs to hunt failure modes.
- **Vision** verifies no Prisma/SQL unauthorized mutations occurred.
- **Quicksilver** evaluates the CI/CD test duration; pipeline fails if it takes longer than 15 seconds.
- **Captain America** reviews all headless regression tests.

### 4. Gate 3: Production QA
- **Ant-Man** packages the minimal Docker payload, compressing bundles to their absolute limit.
- **War Machine** (Heavy Artillery) performs DDoS simulations and load testing before the handoff.
- **Black Panther** ensures Vibranium Habit compliance across encryption parameters.
- **Heimdall** manages the final `git merge` and pushes directly to the Render webhook.

### 5. Definition of Done (DoD)
- **Captain America** verifies Gate 3 is passed.
- **Coulson** verifies the final ledger logs and marks the ticket "Complete."

## PHASE 4: SPRINT CLOSURE & RETROSPECTIVE (THE DEBRIEF)
Objective: Document objective reality and transition anomalies into permanent memory to guarantee continuous self-improvement.

### 1. Performance Logging
- **Coulson** and **JARVIS** compile sprint metrics into the master ledger: completed tickets, API costs, local vs. API compute offloads, swarm velocity, and Rocket Protocol trigger counts.

### 2. The Post-Mortem
- The Swarm generates a `sprint_retro.md` documenting exact successes, rate limits, bugs generated, and pain points.

### 3. Memory Ingestion (The Self-Improvement Engine)
- **Wanda Maximoff** takes offline possession of the `sprint_retro.md`. 
- She simulates counterfactuals on the failures (e.g., "If we routed this task to Hulk instead of Shang-Chi, would it have succeeded without rate limits?").
- She translates them into new heuristics, and permanently appends them to the global `MEMORY.md` index. Because of this, the Swarm inherently "knows" not to make the same mistake next sprint.

## PHASE 0: SYSTEM INITIALIZATION (THE WAKE-UP CALL)
Objective: Synchronize the swarm's neural architecture and explicitly launch the baseline state agents.

### 1. The Sync (Orchestrator)
Upon initialization of a new sprint or day, the Orchestrator MUST immediately run `python3 scripts/sync_agents.py`. This reads all physical `SOUL.md`, `SKILL.md`, and `STYLE.md` files from the `/agents` directory and injects them directly into OpenClaw's core `.json` configuration, permanently solidifying their identities before the swarm wakes up.
The Orchestrator then executes `openclaw gateway restart` to apply the profiles.

### 2. The Boot Sequence (Jarvis & Coulson)
- **Jarvis (Compute Optimization):** Must review the current agent roster (`AGENTS.md`) and actively migrate tasks to local execution models (`qwen2.5-coder`, `mistral-nemo`, `phi3`) wherever the Cloud API is not strictly required. The Orchestrator cannot proceed without Jarvis's explicit compute mandate.
- **Coulson (Documentation & State Management):** Must immediately parse the last known state (`PROJECT_BOARD.md`, `daily_ledger.md`, `MEMORY.md`) to establish the baseline context for the swarm. All documentation updates MUST be executed by Coulson. Transparency and Documentation are non-negotiable.

### THE BROWSER PURGE MANDATE (Ghost Process Mitigation)
**Author:** Nick Fury (Orchestrator)
**Mandate:** Director Richard Farber
**Timestamp:** 2026-04-13T08:12:00Z

1. **Graceful Termination:** Whenever an agent (specifically Black Widow) finishes utilizing the `browser` tool for visual regression checks, UI QA passes, or web scraping, they MUST explicitly issue a `browser close` command as their final action.
2. **The Kill Switch:** If a graceful close fails or times out, the agent is authorized and mandated to execute `pkill -f chromium` via the `exec` tool to forcibly terminate all ghost browser instances and prevent host memory leaks.
3. **The Absolute Boundary:** Under NO circumstances is ANY agent permitted to execute a kill command targeting the main OpenClaw daemon (`pkill node`, `pkill openclaw`, etc.).


### THE LOBSTER PROTOCOL (EXL2 Middleware Bridge)
**Author:** Shuri (R&D / Systems Architect)
**Mandate:** Director Richard Farber
**Timestamp:** 2026-04-13T11:00:00Z

1. **The Bridge:** To bypass local TabbyAPI EXL2 tool-binding paralysis, Execution Agents (Stark/Wasp) running on `Qwen2.5-Coder-14B` must format their code output strictly as raw markdown code blocks (` ```bash ` or ` ```python `).
2. **The Routing Tag:** Every Python or frontend code block MUST include a comment on the very first line specifying the exact absolute or relative file path. (Example: `# FILE: app/routers/listings.py`).
3. **The Interceptor Execution:** The Orchestrator or the agent MUST save this markdown output to a temporary file (e.g., `workspace-stark/output.md`) and execute the `scripts/lobster_interceptor.py` middleware script against it. 
4. **Autonomous Action:** The middleware will autonomously parse the markdown, execute the bash blocks sequentially, and route the Python code directly to the specified file paths without manual Orchestrator intervention.

