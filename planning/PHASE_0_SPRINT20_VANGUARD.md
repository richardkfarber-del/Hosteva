# Phase 0: Vanguard Planning (Sprint 20: Comms & TDD)
**Date:** 2026-04-16
**Goal:** Architect the Telegram Webhook (FEAT-018) and the Pytest State Isolation Infrastructure (TECH-004).
**Targets:** FEAT-018, TECH-004

## Vanguard Consensus & Architectural Alignment

**Spider-Man (Automation Scripter):** 
"For FEAT-018 (Telegram Webhook), I will write a lightweight synchronous function inside `system/swarm_worker.py` (e.g., `send_telegram_alert`). The daemon will call it exclusively when a ticket hits `DONE`, `REJECTED`, or `FAILED_ESCALATED`. To satisfy She-Hulk's PII mandate, I will strip the raw JSON payload and only POST the `[Ticket Number] - [Agent] - [Status]` string. The `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` will be explicitly pulled via `os.environ`."

**Iron Man (CTO - Architecture):** 
"For TECH-004 (Pytest Infrastructure), Shuri and I will build the `tests/conftest.py` file. The test environment MUST NOT mutate the development database. We will configure an `override_get_db` dependency injection for FastAPI to point to an ephemeral SQLite in-memory database (`sqlite:///:memory:`) for all endpoints. For the Redis Streams state machine, we will utilize the `fakeredis` pip package to guarantee perfect isolation."

**Black Widow (QA Shadow):** 
"An in-memory SQLite database drops natively after the test suite finishes, which satisfies my teardown requirement. However, SQLite does not support Postgres ENUMs (`ticket_status`) natively. Iron Man must ensure the SQLAlchemy models dynamically map the ENUM to `VARCHAR` during testing, or the `pytest` initialization will crash."

**She-Hulk (CLO - Compliance):** 
"Spider-Man's PII-stripping logic is sound. Telegram is outside our jurisdiction; raw application data must not cross that boundary. The webhook is approved."

**Hawkeye (Product Owner):** 
"The strategy is aligned. Cap's constraints are met. I've locked FEAT-018 and TECH-004 onto the board."