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
- If the Swarm cannot autonomously resolve a dependency, it triggers a Hard Stop and Fury escalates to the Secretary (Director).

### 4. The Lock (Captain America & Coulson)
- Captain America confirms feasibility.
- Coulson logs the official sprint manifest and start state in the ledger.
- No ad-hoc scope changes are permitted without restarting this phase.

## PHASE 3: EXECUTION & MULTI-STAGE QA (THE GAUNTLET)
Objective: Write the code and prove it works at three distinct layers of integration using pointer-handoffs.

### 1. Execution Loop
Wasp, Shang-Chi, or Hulk execute the code on a local branch. They save the files and pass the file paths to Coulson. Coulson logs the commit state and hands the paths to QA.

### 2. Gate 1: Local Feature QA
- **Black Widow** silently sweeps the isolated branch files for vulnerabilities.
- **She-Hulk** audits the reasoning chain to ensure the dev didn't hardcode a shortcut just to pass the test.
- **Hawkeye** runs tests.
- **The Rocket Trigger Check:** If the build fails to compile or fails QA twice in a row, Rocket steps in, diagnoses, and halts the swarm for your review. Requirement: Zero critical failures.

### 3. Gate 2: Local Integration QA
- The code is merged locally.
- **Winter Soldier** runs the Golden Master regression suite to ensure no legacy/Hosteva breakages.
- **Vision** verifies no Prisma/SQL unauthorized mutations occurred.
- **Coulson** documents the test output paths. Requirement: Successful local boot, zero regressions.

### 4. Gate 3: Production QA
- **Ant-Man** packages the minimal Docker payload.
- **War Machine** handles the deployment to the Render environment.
- **Black Panther** verifies end-to-end encryption standards hold.
- A final, live-environment smoke test is conducted.

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
