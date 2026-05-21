# Phase 0: Vanguard Planning (Sprint 20: TDD Spike & Webhook)
**Date:** 2026-04-16
**Goal:** Architect the Telegram Webhook (FEAT-018) and evaluate Pytest Infrastructure (SPIKE-008).
**Targets:** FEAT-018, SPIKE-008

## Vanguard Consensus & Architectural Alignment

**Spider-Man (Automation Scripter):** 
"For FEAT-018, the Telegram bot API is dead simple. I will use the `requests` library to fire a `POST` to `https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage`. I will intercept the ticket state inside the `swarm_worker.py` daemon right after a ticket transitions. If the `status` is `DONE`, `REJECTED`, or `FAILED_ESCALATED`, I format the string and fire the payload."

**Black Panther (CISO):** 
"For FEAT-018, the webhook payload must NOT dump the `data` dictionary. Only send: `[ticket_id] - [agent_name] - [status] - [coulson_audit_summary]`. This prevents any raw JSON PII from hitting Telegram's servers."

**Shuri (Platform Engineering & R&D):** 
"For SPIKE-008, the Secretary is entirely correct. We cannot use SQLite `:memory:` for our test suite. Vision just added `EXCLUDE USING gist (valid_period WITH &&)` and `tsrange` to the PostgreSQL `property_compliance` table. SQLite does not have a `tsrange` type or a GiST index. If we try to run `Base.metadata.create_all(bind=engine)` on an SQLite dialect, SQLAlchemy will throw a fatal `CompileError`."

**Iron Man (CTO - Architecture):** 
"Shuri's analysis is final. To execute TECH-004, we MUST spin up a secondary `test_db` PostgreSQL container inside `docker-compose.yml` (e.g., mapped to port `5433`). The `tests/conftest.py` file will override the `get_db` dependency to point to `postgresql+psycopg://user:pass@localhost:5433/test_db`. To handle Thanos's state isolation, the `conftest.py` fixture will yield a database connection wrapped in a transaction, and then execute `session.rollback()` in a `finally` block after every single test. This is mathematically faster than dropping and recreating the tables."

**Hawkeye (Product Owner):** 
"The strategy is aligned. I've updated the constraints. The tickets on the board accurately reflect these architectural mandates."