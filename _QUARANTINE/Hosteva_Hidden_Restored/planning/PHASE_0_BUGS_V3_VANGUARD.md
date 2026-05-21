# Phase 0: Vanguard Planning (Crucible Terminal Hotfixes)
**Date:** 2026-04-16
**Goal:** Seal the final architectural desyncs (State Matrix Keys & Queue Atomicity).
**Targets:** BUG-013, BUG-014

## Vanguard Consensus & Architectural Alignment

**Iron Man (CTO - Architecture):** 
"For BUG-013, this is a strict Python dictionary patch. I will add `"DONE": []` and `"FAILED_ESCALATED": []` to `ALLOWED_TRANSITIONS`. This ensures `current_state in ALLOWED_TRANSITIONS` always evaluates to True, trapping the terminal states perfectly. For BUG-014, we must wrap the state transition in a Redis `pipeline()`. The `rpush` and `lrem` will execute atomically."

**Vision (Data Engineer):** 
"For the BUG-014 sweeper concurrency issue, a blind drain is lethal if we scale. We will add a timestamp to the JSON payload. The sweeper will only recover tasks that have been in the processing queue longer than a dead-letter timeout (e.g., 5 minutes). Active tasks won't be stolen."

**She-Hulk (CLO - Compliance):** 
"Atomicity guarantees are mandatory for our audit logs. Ensure the pipeline executes cleanly so we never log duplicate state transitions in the Postgres ledger."

**Hawkeye (Product Owner):** 
"The targets are perfectly aligned. Cap's constraints are met. I've locked BUG-013 and BUG-014 onto the board."