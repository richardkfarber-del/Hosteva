# HOSTEVA SWARM DIRECTIVES

## 1. THE DYNAMIC WORKFLOW RULE
**NEVER HARDCODE TICKET-SPECIFIC CONTEXT INTO ORCHESTRATOR SCRIPTS.**

* **Violation:** Hardcoding specific bug details (e.g., "check for Jinja2 syntax", "look for the logo bug") into the `scrum_pipelines/*.py` files.
* **Standard:** All orchestrator scripts and agent prompts MUST be 100% dynamic. Agents must derive their context *exclusively* from `swarm_state.json`, Git diffs, and the artifacts passed from previous phases.
* **Enforcement:** Any agent or human caught hardcoding task-specific context into a pipeline script to force a pass/fail will trigger an immediate pipeline halt and audit.
