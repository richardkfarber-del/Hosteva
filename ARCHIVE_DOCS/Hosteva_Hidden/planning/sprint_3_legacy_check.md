# Sprint 3 Legacy Testing Check & Risk Assessment

## 1. Legacy Characterization Tests Required
Yes, legacy characterization tests are **highly required**. Before executing schema migrations on the existing `properties` schema or altering database concurrency settings, we must capture the existing baseline behavior.
*   **Property Schema Behavior:** Tests must lock down how properties are currently created, updated, and retrieved so that the transition to a 1-to-many `property_listings` relationship does not break existing property lookups.
*   **Core Pipeline Performance:** Characterization tests for the Address Eligibility and Subscription Gateway pipelines must be established to monitor database access latency and success rates under current loads, ensuring future async tasks don't degrade these critical paths.

## 2. Risk Assessment: Schema Migration (1-to-Many & OAuth)
*   **Data Integrity Risk [HIGH]:** Modifying the core `properties` schema to support the new `property_listings` (1-to-many) relationship carries a high risk of orphan records or data mapping errors if foreign keys are not strictly enforced during migration.
*   **OAuth Token Security [HIGH]:** Introducing OAuth token storage schemas adds highly sensitive credentials to the database. If the SQLite database is not properly encrypted or separated, it poses a major security vulnerability.
*   **Rollback Complexity [MEDIUM]:** SQLite migrations (especially dropping or modifying columns) can be complex because SQLite does not support all `ALTER TABLE` commands natively. It often requires table recreation and data copying, which increases migration failure risk.

## 3. Risk Assessment: SQLite Thread Locks & Async Task Queues
*   **Lock Contention / DB Busy Errors [HIGH]:** SQLite utilizes file-level locking. Concurrent writes—which will surge when background workers asynchronously push/pull to Airbnb and VRBO APIs—will likely result in `database is locked` (SQLITE_BUSY) exceptions.
*   **Pipeline Disruption [CRITICAL]:** The existing synchronous pipelines—**Address Eligibility** and **Subscription Gateway**—rely on immediate database availability. If background workers hold write locks while updating listing statuses or logging API retries, users attempting to process subscriptions or check eligibility will experience timeouts and application crashes.
*   **Mitigation Strategy Required:** 
    1. Ensure **SQLite WAL (Write-Ahead Logging)** mode is explicitly enabled to allow concurrent reads alongside writes.
    2. Enforce a strict timeout/retry policy on database connection parameters to handle temporary locks gracefully.
    3. Keep background worker state (e.g., Celery broker/backend) strictly in Redis and avoid writing temporary task states to the main SQLite database.
    4. Consider evaluating a migration to a fully concurrent database (like PostgreSQL) if the write-load scales beyond SQLite's single-writer limitation.