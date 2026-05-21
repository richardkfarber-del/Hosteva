# THE HOSTEVA SPRINT PROCESS

## Phase 1: Backlog Refinement (The Crucible)
**Objective:** Ensure absolute clarity, strict formatting, and architectural consensus before a ticket reaches a sprint.

1. **The Draft:** Hawkeye (PM) drafts the ticket in an isolated .md file, strictly adhering to formatting:
   - **User Stories:** 3rd-person Gherkin syntax only (e.g., "Given a user is..."). Never first-person.
   - **Tech & Spike Tickets:** Strict bulleted list Acceptance Criteria (AC). No Gherkin.
   - **Bug Tickets:** "Expected Behavior" single sentence or bullet list. No Gherkin.
2. **Coulson's Gate:** Hawkeye passes the file path to Coulson. Coulson audits the formatting. If perfect, Coulson logs the draft and opens the Swarm Review.
3. **The Swarm Review:** Coulson routes the file path to Vision/Stark (Architecture) and Captain America (Agile Lead).
4. **The Lock:** Reviewing agents must append their "Approved" stamp or actionable feedback directly into the ticket file. Once all approve, Captain America seals the ticket and Coulson logs the "Ready" state.

## Phase 2: Sprint Planning (The War Room)
**Objective:** Establish consensus, identify blockers, lock the scope, and log the state.

1. **The Proposal:** Fury reads the locked backlog and presents the proposed sprint payload (via file paths) to the active Swarm.
2. **Consensus & Capacity Check:** JARVIS models the compute/token cost. Winter Soldier checks if legacy characterization tests are needed. All executing agents review the target file paths against their capacities.
3. **Escalation Protocol:** Any negative feedback triggers an immediate revision. If the Swarm cannot autonomously resolve a dependency, it triggers a Hard Stop and Fury escalates to the Director.
4. **The Lock:** Captain America confirms feasibility. Coulson logs the official sprint manifest and start state in the ledger. No ad-hoc scope changes are permitted.

## Phase 3: Execution, CI/CD, & The Bifrost (The Gauntlet)
**Objective:** Devs code, Architects approve, Testers break, Release deploys, and Product verifies.

1. **The Build (The Makers):** Wasp (Frontend), Shang-Chi (Full-Stack), or Hulk (Backend) are assigned as the active developers. They read the ticket, write the actual code modifications in an isolated local feature branch, save the files, and pass the file paths to Coulson. Coulson logs "Code Complete."
2. **Architecture Review (The PR Gate):** Coulson routes the file paths to Iron Man (System) and Vision (Database). They review the code for structural integrity, schema rules, and Big O efficiency. If rejected, it routes back to Devs. If "Approved", Coulson routes to QA.
3. **Gate 1 - Local Technical QA (The Testers):** Coulson routes to Black Widow. She executes automated test suites and vulnerability sweeps against the files. She-Hulk audits the reasoning chain. (Rocket Two-Strike Failsafe is active here). Requirement: Zero critical failures.
4. **Gate 2 - Legacy Regression Gate:** Coulson routes to Winter Soldier. He runs Golden Master regression suites against the feature branch to ensure legacy/Hosteva connections remain stable. Requirement: Zero regressions.
5. **Gate 3 - The Bifrost (Enter Heimdall):** Devs and Testers are locked out. Coulson hands the approved branch to Heimdall. Heimdall executes the Git merge to main, pushes to the remote repo using his keys, and monitors the Render CI/CD webhooks. Once a 200 OK stable boot is returned, Heimdall broadcasts the "Release Complete" signal.
6. **Gate 4 - Production UAT (Product Verification):** Triggered by Heimdall, Black Widow runs a live-environment smoke test. Hawkeye steps in to perform User Acceptance Testing (UAT) by visually inspecting the deployed Render URL as a human user.
7. **Definition of Done (DoD):** Hawkeye gives final Product Approval. Captain America verifies no chain-of-custody breaks occurred. Coulson seals the ledger and marks the ticket "Complete."

## Phase 4: Sprint Closure & Retrospective (The Debrief)
**Objective:** Document objective reality and transition behavioral anomalies into permanent memory.

1. **Performance Logging:** Coulson and JARVIS compile sprint metrics into the master ledger: completed tickets, API costs, compute offloads, swarm velocity, and Rocket Failsafe triggers.
2. **The Post-Mortem:** The Swarm generates a `sprint_retro.md` documenting exact successes, rate limits, bugs generated, and pain points.
3. **Memory Ingestion (The Software Update):** Wanda Maximoff takes offline possession of `sprint_retro.md`. She simulates counterfactuals on failures, translates them into new behavioral heuristics, and permanently appends them to the global `MEMORY.md`.
4. **Clean Slate:** Each agent summarizes everything they did in the past sprint to their daily ledger, then wipes their short-term memory, context, and tokens to start the next sprint fresh.

## Phase 5: Executive Review & Swarm Evolution (The C-Suite)
**Objective:** Strategic analysis, R&D capability augmentation, and continuous Director-approved evolution.

1. **The R&D Innovation Sweep (Enter Shuri):** Shuri (R&D Toolsmith) reviews the sprint retrospective. She actively researches external AI capability upgrades (new MCP servers, custom CLI scripts, new skills, or AI model routing swaps) to solve the exact bottlenecks the Swarm experienced.
2. **The Vanguard Check:** Kang reviews Shuri's proposals against deprecation schedules (TC39/RFCs) to prevent tech debt. Falcon inputs external market trends.
3. **The Capability Proposal:** Shuri drafts a formal Swarm Upgrade Proposal (`rnd_upgrades.md`) with exact tools, ROI, and installation instructions. She passes the path to Coulson.
4. **The Director's Briefing:** Fury compiles the retrospective, Wanda's memory updates, and Shuri's Swarm Upgrade Proposal into an `executive_summary.md`. Fury halts the Swarm and presents this briefing directly to ME (The Secretary).
5. **The Forge (Final Escalation):** The Secretary manually Approves or Denys the proposed tooling upgrades. If approved, Shuri and Rocket execute the tool installations. The Sprint officially closes, and the swarm powers up for the next sprint fundamentally better equipped.
