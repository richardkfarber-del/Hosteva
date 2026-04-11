# Hosteva Swarm: The Golden Pipeline

This document defines the absolute, unalterable process for all code generation, testing, and deployment. This must be referenced and enforced across all restarts and days.

## GLOBAL PROTOCOLS
* **Coulson's Ledger Mandate:** EVERY agent, at EVERY step, MUST document the result of their task (success or failure, compute used, notes) in `daily_ledger.md`. Phil Coulson will audit the ledger between *every single step*. Progress is blocked until Coulson verifies the paperwork. This data fuels Wanda's Dreamstate heuristic for swarm evolution.
* **The Rocket Failsafe:** If ANY agent fails at ANY point in this pipeline, Rocket Raccoon is automatically dispatched to diagnose the failure and suggest a resolution to the Director before the Swarm attempts to retry.

## Phase 1: Engineering
1. **Hawkeye:** Generates the Ticket on `PROJECT_BOARD.md` and marks it `> CURRENT_FOCUS_TARGET`. Logs to ledger. Coulson audits.
2. **Captain America:** Validates the ticket against the Definition of Ready. Logs to ledger. Coulson audits.
3. **Stark / Wasp:** Executes the code/design. **Mandatory:** The agent MUST explicitly commit their own local changes to Git before logging completion. Heimdall is a gatekeeper, not a janitor. Logs to ledger. Coulson audits.

## Phase 2: Local Pre-Merge QA
4. **Black Widow (QA):** Tests the executed code locally. Logs to ledger. Coulson audits.
   - **[FAIL]:** Negative feedback -> Director + Hawkeye -> Bug Ticket -> Cap Approval -> Stark fixes.
   - **[PASS]:** Proceeds to Local Merge.

## Phase 3: Local Merge & Post-Merge QA
5. **Heimdall (Release Manager/Git Sentinel):** Acts as the strict Git Sentinel. Before merging approved code into the local `main` branch, Heimdall MUST verify unit test passage, visual QA clearance, and LOBSTER.md compliance (no bloated diffs). Logs to ledger. Coulson audits.
6. **Black Widow (QA):** Tests the merged code locally on the `main` branch to ensure no integration regressions. Logs to ledger. Coulson audits.
   - **[FAIL]:** Immediate Bug Ticket loop.
   - **[PASS]:** Proceeds to Live Deployment.

## Phase 4: Live Deployment & UAT QA
7. **Heimdall (Release Manager):** Executes `git push origin main` to trigger the Render auto-deploy. Logs to ledger. Coulson audits.
8. **Black Widow (QA):** Runs full test suite directly on the live UAT site (`https://hosteva.onrender.com/`). Logs to ledger. Coulson audits.
   - **[RENDER FAILSAFE]:** Black Widow MUST use the `browser` or `exec curl` tool to poll the live site and verify a specific UI element or version string has changed BEFORE beginning the QA pass, OR she must wait for explicit confirmation that the Render build has succeeded.
   - **[FAIL]:** Immediate Bug Ticket loop.
   - **[PASS]:** No negative feedback. Final QA Approval granted.

## Phase 5: The Victory Condition
9. **Coulson:** Marks the Sprint/Epic as DONE on the board.
10. **Swarm:** CELEBRATE.

## Phase 6: The Sprint Retrospective Protocol (Strategic Review)
11. **Jarvis's Compute Audit:** Jarvis must generate a Token Usage & Efficiency Report covering the sprint.
12. **Wanda's Stability Report:** Wanda will review the `daily_ledger.md` using her Dreamstate heuristics and provide a Stability Report, identifying systemic friction points.
13. **Hawkeye's Velocity Review:** Hawkeye reviews the completed tickets to ensure scope was adhered to and business value was actually delivered.
14. **Coulson's Compliance Audit:** Coulson verifies that all agents successfully adhered to the ledger mandate without requiring Rocket's intervention.
15. **Bruce Banner's R&D Discovery:** Acting as Lead R&D Scientist, Banner takes Wanda's friction points and Jarvis's compute reports, uses web tools to scour the internet, and presents actionable upgrades (new tools, updated models, prompt strategies, or architectural shifts).
16. **Executive Decision Matrix:** Fury aggregates all reports and delivers them to the Director. NO new sprint can begin, and NO memory flush can occur, until the Director reviews the retrospective and approves any necessary swarm adjustments.

## Phase 7: The Sprint Flush (Memory Management)
17. **The Retrospective Ledger:** Upon Sprint completion and Executive approval (Phase 6), EVERY agent involved in the sprint must write a brief, narrative update to `daily_ledger.md`. This entry must detail exactly what they executed, what went wrong (friction points), what went well, and what was ultimately completed. 
18. **The Orchestrator's Log:** Nick Fury must independently write all system-level process updates, newly established rules, and pipeline modifications to the ledger.
19. **The Purge:** Once the Retrospective Ledger is complete, all agents (including Nick Fury) must undergo a short-term memory flush (session context purge) to reset token bloat for the next Sprint.

## AMENDMENT: The Rocket Failsafe (Diagnostic Mandate)
* If an agent fails a task (e.g., Stark failing to write to the ledger), Rocket Raccoon MUST NOT bypass the block by doing the work for them. 
* Rocket's mandate is purely diagnostic and infrastructural: he must investigate *why* the agent failed (e.g., token limits, bad prompt injection, missing tools) and implement a permanent, systemic solution so the agent can succeed on retry.

## Stark's Deployment Protocol
- **Mandate:** Stark MUST use ACPx (OpenClaw ACP runtime) utilizing dedicated coding agents (e.g., Aider, Codex, Claude Code) for all file modifications. Standard subagent file manipulation is prohibited to prevent aggressive overwrites and UI regressions.

## Black Widow's QA Protocol
- **Visual QA Vision Models:** When performing visual regression checks on the UI, Black Widow must utilize local vision models (Qwen-VL or Llama 3 Vision) via auto-snapshot hooks. If visual diffs exceed a 2% threshold from the baseline, the deployment must be HALTED.
- **Mandate:** Black Widow MUST perform a 'Baseline Visual Regression Check' against `DESIGN_STATE.md` before passing any UI changes. Simulating checks or purely verifying new text additions is prohibited. All prior CSS and Design Tokens must remain intact.
