# Phase 0: Sprint 16 Vanguard Planning
**Date:** 2026-04-16
**Goal:** V3.0 Automation Engine Rewrite

## Vanguard Consensus & Architectural Alignment

**Iron Man (CTO - Architecture):** 
"The current `app/api/routes/swarm.py` and the PostgreSQL enum only recognize the 11 original states. We need to physically write an Alembic migration (or raw SQL init script update) to alter the `ticket_status` ENUM type to accept the new Tollgate states. The `swarm_worker.py` daemon needs to be rewired to route `QA_REVIEW` strictly to Coulson, and we must code the 3-strike integer counter into the Redis payload."

**Vision (Data Engineer):** 
"Agreed. Modifying an existing Postgres ENUM in production can be tricky. We will write a dedicated schema update script in `/app/scripts/` to execute the `ALTER TYPE` command safely without dropping the existing table data."

**She-Hulk (CLO - Compliance):** 
"To satisfy the Threat Council mandate and future SOC2 audits, the backend must permanently log the Threat Council's approval timestamp. The state machine cannot permit the `DREAMSTATE_READY` status unless the security audit payload is cryptographically present."

**Falcon (Market Recon):** 
"Moving to a strict, multi-stage state machine aligns with enterprise GitOps patterns (like Linear or Jira workflows). If we ever need to bridge OpenClaw's internal state to an external Jira board, this explicit state-mapping will make the API hook seamless."

**Rocket Raccoon (Fixer):** 
"Just make sure my trigger is wired right. If Coulson hits 'reject' on a ticket 3 times, the daemon needs to dynamically spawn my subagent path and pass me the exact error logs so I can diagnose the environment."

**Hawkeye (Product Owner):** 
"Target acquired. I am writing `TECH-001: V3.0 Automation Engine Rewrite` to the board now. Acceptance Criteria will be strictly bulleted per Cap's rules."