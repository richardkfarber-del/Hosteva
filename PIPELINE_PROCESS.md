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
## Black Widow's QA Protocol (Amendment)
- **Formatting Mandate:** Black Widow MUST use strict markdown headers (`##` or `###`) for every ledger entry to ensure Coulson's parser can accurately detect her reports. Unformatted appends (e.g. raw text with brackets like `[Phase 3]`) are strictly prohibited.

### THE MARKDOWN WRITER MANDATE (Update)
All agents operating on local models (`phi3`, `mistral-nemo`, `qwen2.5-coder`) MUST use `python3 scripts/write_markdown.py` via the `exec` tool for ALL modifications to `PROJECT_BOARD.md` and `daily_ledger.md`. The `edit` and `write` tools are strictly forbidden for markdown files to prevent exact-string matching hallucinations. 

Usage:
`cat << 'MARKDOWN_EOF' | python3 scripts/write_markdown.py <file> --mode append`

### THE AIDER EXECUTION MANDATE
All Execution Agents (Stark, Wasp) running on local coder models (`qwen2.5-coder:7b`) MUST exclusively use the `aider` CLI via the `exec` tool for ALL source code modifications (HTML, CSS, JS, Python). 
Do NOT attempt to use complex Bash commands (`sed`, `cat << EOF`) or the `edit` API tool to modify source code, as local models struggle with strict string escaping and whitespace matching.
**Usage Example:** `aider app/templates/ordinance_directory.html --message "Add javascript fetch logic pointing to /api/ordinances/"`

### THE VISION MANDATE (Phase 1, Step 3)
Before any new Epic enters Phase 3 (Execution), it MUST pass an Architectural Review by Vision. Vision will evaluate the cross-functional Gherkin tickets and define the specific database, infrastructural, and engineering technical paths required to support the feature. Execution agents (Stark/Wasp) must build strictly to Vision's architectural specifications.

### THE MICRO-TASKING DOCTRINE (Nick Fury)
**1. Cloud API Allocation:** Phase 1 (Initial Research, Architectural Review by Vision, and Ticket Generation by Hawkeye) MUST be executed using Cloud API models. They possess the cognitive capacity to define broad scope.
**2. Execution Breakdown:** All execution tickets MUST be broken down into single-file, single-action Micro-Tasks before being handed to local models (Stark, Wasp, Black Widow). Local models are forbidden from multi-file or multi-step batch processing.
**3. Granular Feedback:** Any feedback or rejections from QA (Cap/Black Widow), Architecture (Vision), or Deployment (Heimdall) must be parsed into isolated micro-tasks before being handed back to an execution agent.

### THE EXECUTION BYPASS PROTOCOL & BUG TRACKING
1. **The Python Executor Script:** To prevent Nick Fury from manually injecting code for local 7B models, all future Micro-Tasks that output raw Python or YAML MUST be accompanied by an automated OpenClaw execution script (e.g., `write_code.py <file>`). The Orchestrator will run this script automatically on the model's output block.
2. **Mandatory Bug Tracking:** Any failure caught by QA (Black Widow/Cap), Architecture (Vision), or Deployment (Heimdall) MUST automatically generate a formal `BUG-` ticket in `PROJECT_BOARD.md` before the fix is assigned.

### THE DEFECT DELEGATION PROTOCOL (Update)
The Orchestrator will NO LONGER manually write BUG tickets. 
When QA (Black Widow, Captain America, Coulson) logs a failure or integration error:
1. The Orchestrator will spawn **Hawkeye (Product Planner)** on a Micro-Task.
2. Hawkeye will read the QA Report and generate a formal `BUG-` ticket with strict Gherkin Acceptance Criteria.
3. Hawkeye will output the raw Markdown ticket, which the Orchestrator will pipe into `PROJECT_BOARD.md` via the Markdown Writer script.
4. Only then will Execution Agents (Stark/Wasp) be deployed to fix the bug.

### THE ORCHESTRATOR'S COMMIT MANDATE
The Orchestrator (Nick Fury) is responsible for maintaining the Git history of all structural and procedural artifacts generated outside of Execution Agents (Stark/Wasp). 
Whenever the Orchestrator manually injects code, updates `PROJECT_BOARD.md`, modifies `PIPELINE_PROCESS.md`, or creates utility scripts (e.g., in `scripts/`), the Orchestrator MUST execute a `git add . && git commit -m "chore(infra): [Description]"` command before handing the pipeline back to QA or Release Management.
