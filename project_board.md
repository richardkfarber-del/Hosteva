# Hosteva Project Board

> CURRENT_FOCUS_TARGET: Sprint 22/23: TDD Benchmark & Compliance Engine Implementation (Resumed)

## Active Tickets

### FEAT-019: Automated Test Coverage Generation (TDD Benchmark)
**Type:** Technical
**Description:** The Executive Board has established a strict Test-Driven Development (TDD) Mandate. The MVP Dashboard API and UI components must have complete automated test coverage integrated into the pipeline before proceeding with further feature builds. This ticket establishes the baseline testing infrastructure and coverage metrics for the `GET /api/v1/properties` route and the `dashboard.html` UI component.
**Expected Behavior:** The automated test suite (`pytest`) successfully runs and mathematically verifies the correct masking of PII, authorization boundary handling, and degraded system state UI rendering.
**Acceptance Criteria:**
* The MVP Dashboard API (`GET /api/v1/properties`) must have tests covering positive PII masking response, HTTP 401 unauthorized errors, and simulated HTTP 503 timeouts gracefully handled.
* The MVP Dashboard UI (`dashboard.html`) must have basic Selenium/Playwright scripts (or Pytest DOM checks) verifying `PropertyCardSkeleton` rendering and the "System Degraded" error boundary.
* The automated test suite must pass 100% green via `pytest tests/` before any future code is pushed.

### FEAT-020: Compliance Wizard Backend Models
**Type:** Technical
**Description:** Implement the core PostgreSQL data models and alembic database migrations for the municipal compliance engine. This requires translating the architecture defined in SPIKE-007 into physical SQLAlchemy models, enforcing strict append-only temporal versioning to prevent data overwrites, and applying rigorous GiST and B-Tree indexing strategies for performant spatial/temporal queries.
**Expected Behavior:** The backend models (`municipal_codes` and `property_compliance`) are physically instantiated in the database with strict data constraints, trigger-based history retention, and optimized index structures.
**Acceptance Criteria:**
* The SQLAlchemy models for `municipal_codes` and `property_compliance` are physically present in `app/models/compliance.py` and their respective Alembic database migrations have been successfully executed.
* The `trg_close_expired_compliance` PostgreSQL Trigger is physically implemented to enforce append-only temporal versioning and prevent historical overwrite operations.
* The schema enforces rigorous `CHECK` constraints on strings (e.g., maximum length, regex for ordinance format) for `municipal_codes` to prevent database-level buffer overflows or SQL injection vectors.
* The `property_compliance` table includes composite GiST or B-Tree indexes across `property_id` and the `valid_period` `tsrange` column to mathematically guarantee O(log N) lookup times.

## Backlog
### BUG-001: Render Deployment Halt - Missing Infrastructure and Database URL Rewrite
**Type:** Bug
**Description:** The deployment phase crashed and the Sprint halted. Heimdall rejected the state update due to missing Render infrastructure-as-code files and missing Render database URL rewriting logic required by production deployment rules.
**Expected Behavior:**
* The `render.yaml` infrastructure-as-code file is generated to bridge Docker containers into the Render cloud environment.
* The application logic correctly intercepts Render's `DATABASE_URL` environment variable and rewrites it to the `postgresql+psycopg://` schema.
* The system passes Heimdall's Render Production Deployment Hard Rules validation.
