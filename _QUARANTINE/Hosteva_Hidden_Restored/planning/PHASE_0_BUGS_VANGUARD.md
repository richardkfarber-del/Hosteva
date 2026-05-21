# Phase 0: Vanguard Planning (Crucible Bug Fixes)
**Date:** 2026-04-16
**Goal:** Harden the V3.0 State Machine Architecture against Crucible failures.
**Targets:** BUG-005, BUG-006, BUG-007, BUG-008

## Vanguard Consensus & Architectural Alignment

**Iron Man (CTO - Architecture):** 
"For BUG-007 (State Matrix), we need to hardcode a valid state transition dictionary in `swarm.py`. If `current_state == BUILDING`, the only valid next states are `AUDITING` or `FAILED`. Anything else gets a 400. For BUG-005, we need to enforce a shared secret or cryptographic token in the headers, not just a payload key."

**Vision (Data Engineer):** 
"For BUG-006 (Reliable Queue), shifting from `BLPOP` to `BRPOPLPUSH` means we need a secondary 'processing' queue. If the daemon crashes, the task remains in the processing queue and we can build a recovery script to sweep it back to the main queue on startup."

**Shang-Chi (Clean Architecture):** 
"For BUG-008, parsing raw LLM text for 'VERIFIED' is inherently brittle. We need to enforce a strict JSON output schema from Coulson (e.g., `{"audit_status": "VERIFIED", "reason": "..."}`). The daemon will parse the JSON instead of relying on string matching."

**She-Hulk (CLO - Compliance):** 
"The cryptographic token for BUG-005 must be rotated or securely injected via environment variables. Do not hardcode the secret in the repository, or we fail the security audit anyway."

**Falcon (Market Recon):** 
"These fixes align with enterprise robust queue patterns (like Celery/RabbitMQ, but native to Redis). It's a standard and necessary architectural maturation."

**Hawkeye (Product Owner):** 
"The targets are perfectly aligned. I am enforcing Cap's formatting rules on BUG-005 through 008 now. They are locked on the board."