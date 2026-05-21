# Phase 0: Vanguard Planning (Crucible Hotfixes)
**Date:** 2026-04-16
**Goal:** Seal the edge-case exploits exposed in the first Crucible re-test.
**Targets:** BUG-009, BUG-010, BUG-011, BUG-012

## Vanguard Consensus & Architectural Alignment

**Iron Man (CTO - Architecture):** 
"For BUG-009, we don't just use `os.environ['DREAMSTATE_TOKEN']` in the route—we enforce it at the FastAPI startup event. If the environment variable is missing, the app fails to boot. Fail closed. For BUG-011, I will explicitly map `DONE` and `FAILED_ESCALATED` as legal transitions out of the `AUDITING` state."

**Vision (Data Engineer):** 
"For BUG-010, I will implement a startup sweeper in the daemon. Before entering the main `while True` loop, the worker will use `LMOVE` (or `RPOPLPUSH`) to drain `swarm:queue:processing` completely, pushing any ghost tasks back to `swarm:queue:tasks`. We will also restore atomic Redis tracking for the strike counter so it survives drops."

**Shang-Chi (Clean Architecture):** 
"For BUG-012, we add an explicit `if not isinstance(parsed_data, dict):` check immediately after `json.loads()`. If it's a list or a string, we manually push the raw payload to the DLQ and `continue` the loop, completely avoiding the `AttributeError`."

**She-Hulk (CLO - Compliance):** 
"Failing closed on the missing environment variable satisfies our strict security mandates. Ensure the DLQ routing for malformed JSON logs the incident without exposing sensitive payload data."

**Hawkeye (Product Owner):** 
"The strategy is aligned. The tickets on the board accurately reflect these architectural mandates."