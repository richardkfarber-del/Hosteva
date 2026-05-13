# V3 WORKFLOW MASTER ARCHITECTURE

This document defines the immutable 13-phase GraphBit pipeline, agent roster, bound skills, and external MCP tool configurations for the Hosteva Swarm.

## PIPELINE PHASES & ROSTER MAPPING

### PHASE 1: Intake (`01_intake.py`)
* **Focus:** Harvesting raw business requirements, enterprise context, and competitive market parameters.
* **Roster:** AGENT-07-PRODUCT (Hawkeye), AGENT-20-RECON (Falcon)
* **Skills:** `business_analysis_skill.md`, `market_recon_research_skill.md`
* **MCP/Tools:** ChromaDB MCP Server (enterprise facts), Web Search MCP (industry constraints)
* **Rule:** Orchestrator (Nick Fury) strictly manages state payload aggregation and does not execute analysis.

### PHASE 2: Sprint Planning & Architecture (`02_planning.py`)
* **Focus:** Collaborative design phase establishing API contracts, data models, compliance boundaries, and UI specs.
* **Roster:** AGENT-10-DATA_ARCHITECT (Vision), AGENT-23-STRATEGIST (Kang), AGENT-18-COMPLIANCE (She-Hulk), AGENT-04-FRONTEND (Spider-Man), AGENT-24-MARKETING (Star-Lord)
* **Skills:** `architecture_skill.md`, `legal_compliance_audit_skill.md`, `ui_ux_specification_skill.md`
* **MCP/Tools:** Gemini API Override Node, Google Stitch MCP
* **Rule:** Assert PII/GDPR constraints immediately. Extract design DNA tokens before execution.

### PHASE 3: Backlog Grooming (`03_backlog.py`)
* **Focus:** Writing and refining repository ticket files.
* **Roster:** AGENT-07-PRODUCT (Hawkeye), AGENT-28-COMPLIANCE (Phil Coulson)
* **Skills:** `backlog_grooming_skill.md`
* **MCP/Tools:** Backlog.md MCP Server
* **Rule:** Absolute taxonomy validation (3rd-person BDD/Gherkin for user stories, bulleted lists for tech/bug tickets).

### PHASE 4: Test-Driven Development Setup (`04_tdd.py`)
* **Focus:** Compiling deterministic test binaries (Playwright/Pytest) before implementation.
* **Roster:** AGENT-08-QA (Black Widow)
* **Skills:** `qa_generation_skill.md`
* **MCP/Tools:** Docker MCP Server
* **Rule:** Provision pristine mock states. Coulson does not execute QA generation.

### PHASE 5: Core Execution (`05_execution.py`)
* **Focus:** Source code implementation.
* **Roster:** AGENT-05-BACKEND (Iron Man), AGENT-12-PRINCIPAL (The Hulk), AGENT-14-FRONTEND (Wasp), AGENT-16-FULLSTACK (Shang-Chi)
* **Skills:** `core_implementation_skill.md`
* **MCP/Tools:** GitHub MCP
* **Rule:** Enforce SOLID/DRY principles. Inject `kickback_context` from `swarm_state.json` if downstream errors occurred.

### PHASE 6: Logic & Pull Request Review (`06_review.py`)
* **Focus:** Validating source code against state machines, routing logic, and architectural contracts.
* **Roster:** AGENT-06-LOGIC (Captain America)
* **Skills:** `pr_review_skill.md`
* **Rule:** If `### 🔴 [BLOCKING]` is emitted, execute `sys.exit(1)` to trigger the orchestrator's kickback loop.

### PHASE 7: Security & Compliance Gates (`07_security.py`)
* **Focus:** Static code analysis, vulnerability scanning, and license governance.
* **Roster:** AGENT-19-SECURITY (Black Panther), AGENT-21-REDTEAM (Ultron), AGENT-18-COMPLIANCE (She-Hulk)
* **Skills:** `security_audit_skill.md`, `legal_compliance_audit_skill.md`
* **MCP/Tools:** OWASP MCP Server
* **Rule:** Halt DAG with `sys.exit(1)` on `### 🔴 [BREACH DETECTED]` or `### 🔴 [COMPLIANCE VIOLATION]`.

### PHASE 8: Deployment & Infrastructure (`08_deploy.py`)
* **Focus:** Immutable builds, artifact tagging, container lifecycles, and live cloud staging.
* **Roster:** AGENT-27-RELEASE (Heimdall), AGENT-09-DEVOPS (Rocket Raccoon)
* **Skills:** `deployment_infrastructure_skill.md`
* **MCP/Tools:** Docker MCP Server, Render MCP Server
* **Rule:** Require sustained HTTP 200 OK health check payload before marking successful.

### PHASE 9: User Acceptance Testing (`09_uat.py`)
* **Focus:** Validating live UI/UX rendering against design variables.
* **Roster:** AGENT-04-FRONTEND (Spider-Man), AGENT-14-FRONTEND (Wasp)
* **Skills:** `ui_ux_specification_skill.md`
* **Rule:** Run runtime design token assertion scripts.

### PHASE 10: Sprint Retrospective (`10_retro.py`)
* **Focus:** Harvesting runtime DAG execution metrics and node efficiency telemetry.
* **Roster:** AGENT-25-AIOPS (Jarvis), AGENT-22-CHAOS (Thanos)
* **Skills:** `retrospective_telemetry_skill.md`
* **MCP/Tools:** ChromaDB MCP
* **Rule:** Route metrics into persistent vector storage. Coders/Product owners do not participate.

### PHASE 11: Memory Consolidation (`11_memory.py`)
* **Focus:** Updating persistent system counterfactuals and logging technical debt.
* **Roster:** AGENT-02-DREAMSTATE (Wanda), AGENT-15-TECH_DEBT (Winter Soldier)
* **Skills:** `memory_consolidation_skill.md`
* **Rule:** Index structural shortcuts to prioritize future refactoring DAGs.

### PHASE 12: Executive Routing (`12_executive.py`)
* **Focus:** Secure out-of-band stakeholder reporting.
* **Roster:** AGENT-01-DIRECTOR (Nick Fury), AGENT-28-COMPLIANCE (Phil Coulson)
* **Skills:** `team_communication_skill.md`
* **MCP/Tools:** Fast-MCP Telegram/Slack bridge
* **Rule:** Publish concise, sanitized operational metrics.

### PHASE 13: Consolidation & Marketing (`13_consolidation.py`)
* **Focus:** Outbound release note synthesis.
* **Roster:** AGENT-24-MARKETING (Star-Lord)
* **Skills:** `marketing_campaign_synthesis_skill.md`
* **Rule:** Synthesize copy strictly from immutable Git commit histories and validated ticket criteria.
