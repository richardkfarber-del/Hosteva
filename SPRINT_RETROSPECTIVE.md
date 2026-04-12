# SPRINT RETROSPECTIVE: Florida V1 Foundation & The Render Crucible

## 1. Velocity & Throughput Metrics
- **Completed Tickets:** 12 (FEAT-011, BUG-002 through BUG-013).
- **Throughput Health:** **MODERATE.** Code generation velocity was exceptionally high, but deployment velocity was severely degraded by environmental disparities and model hallucination loops.
- **Architectural Pivots:** 3 Major (SQLite -> Postgres/pgvector, psycopg2 -> psycopg v3, Global DB Init -> On-Demand Init).

## 2. The Failures & The Fixes (What Went Wrong)
1. **The "Implicit Execution" Hallucination:** Cloud API models (Heimdall, Black Widow) suffered severe context collapse when asked to orchestrate multi-step tool sequences, writing plans in their scratchpads but failing to pull the trigger.
   - *The Fix:* **The "One Gun at a Time" Doctrine.** Cloud models are now strictly limited to executing one tool per turn.
2. **Local Model Tool-Call Paralysis:** Local compute (`qwen2.5-coder:7b`) completely failed to utilize the `exec` tool to write files.
   - *The Fix:* **The Code Writer Delegation.** Local models act purely as "Dumb Muscle," outputting raw code blocks that the Orchestrator intercepts and pipes into the filesystem.
3. **The "Illusion of UAT":** Black Widow initially cleared a deployment because a `curl` health check returned 200 OK, completely ignoring functional API logic and UI rendering.
   - *The Fix:* **The Dual-Pronged QA Doctrine.** UAT now requires both automated `run_uat_regression.py` backend payload testing AND headless browser DOM rendering validation.
4. **Render Deployment Anomalies:** 
   - Global database connections (`CREATE EXTENSION`) in `app/main.py` starved Gunicorn workers (502).
   - Hardcoded port `8000` failed to catch Render's dynamic `$PORT`.
   - Render's native `postgresql://` connection string triggered legacy driver crashes.

## 3. Team & Process Health
- **Process Compliance:** **HIGH.** The Failsafe Absolutism prevented the Orchestrator from masking bad agent logic with manual hotfixes. Forcing the swarm to fix itself resulted in the creation of permanent, scalable automated testing.
- **Context Management:** **FRAGILE.** The overarching lesson of this sprint is that context bloat is fatal. Feeding the entire Project Board and User Profile to an execution agent causes attention dilution. "Context Diets" are mandatory moving forward.

## 4. Recommendations & Future Integrations
1. **Free Tooling (Linting):** Integrate `ruff` (extremely fast Python linter) into the pre-commit hook to catch missing imports (like the Pydantic email validator) before they reach Render.
2. **New Skill Creation (`render-deploy.md`):** Author a formal AgentSkill that mandates parsing `Dockerfile` for dynamic `$PORT` bindings and checking `app/database.py` for `psycopg` v3 string handling before Heimdall is allowed to push to `origin main`.
3. **Dream Cycle Archival:** Consolidate `PIPELINE_PROCESS.md` and these retrospective lessons into `MEMORY.md` to ensure the Orchestrator does not regress into manual execution or global DB initialization in the next cycle.
