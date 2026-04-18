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

## Training Retreat Spikes

### Phase 1: Infrastructure Diet
### CHORE-023: Enforce LF Line Endings for WSL2 Compatibility
**Type:** Technical
**Description:** Configure `.gitattributes` to enforce LF line endings for all text, toml, lock, shell scripts, and Dockerfiles to prevent execution errors in the container.
**Acceptance Criteria:**
* `.gitattributes` file specifies `text eol=lf` for `*.txt`, `*.toml`, `*.lock`, `*.sh`, and `Dockerfile`.
* Commits enforce LF endings for the specified files.

### CHORE-024: Migrate Python Dependencies to pyproject.toml and uv.lock
**Type:** Technical
**Description:** Replace existing `requirements.txt` with modern Python standards (`pyproject.toml` and `uv.lock`) to leverage Astral's `uv` package manager.
**Acceptance Criteria:**
* `pyproject.toml` is created and contains the application's dependencies.
* `uv.lock` is generated to guarantee mathematical reproducibility.
* `requirements.txt` is removed from the project tree.

### CHORE-025: Implement Docker Builder Stage with uv
**Type:** Technical
**Description:** Create the `builder` stage of a multi-stage Dockerfile that pulls the `uv` binary, configures caching, creates a virtual environment, and installs dependencies.
**Acceptance Criteria:**
* The stage starts with `FROM python:3.12-slim AS builder`.
* The `uv` binary is injected via `COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/`.
* `UV_COMPILE_BYTECODE=1` and `UV_LINK_MODE=copy` are set as environment variables.
* A Python virtual environment is created at `/opt/venv` and prepended to `PATH`.
* Dependencies are installed using `uv sync --frozen --no-install-project --no-dev` with BuildKit Cache mounts (`--mount=type=cache`, `--mount=type=bind`).

### CHORE-026: Implement Docker Final Runtime Stage
**Type:** Technical
**Description:** Create the final minimal runtime stage in the Dockerfile, focusing on security via non-root execution and layer size reduction.
**Acceptance Criteria:**
* The stage starts with `FROM python:3.12-slim`.
* `PYTHONUNBUFFERED=1` is configured.
* A non-root user `hosteva_user` is created (`useradd -m -u 1000 hosteva_user`).
* The `/opt/venv` directory is copied from the `builder` stage.
* Source code is copied into `/app` with `--chown=hosteva_user:hosteva_user`.
* The container executes as `USER hosteva_user`.
* `CMD` runs FastAPI (`uvicorn main:app --host 0.0.0.0 --port 8000`).

### CHORE-027: Configure Docker Compose Virtual Environment Isolation
**Type:** Technical
**Description:** Ensure that the Docker Compose configuration explicitly excludes the container's virtual environment from host volume mounts to prevent binary incompatibilities.
**Acceptance Criteria:**
* Docker Compose file contains an anonymous volume mount for `/opt/venv` (or equivalent exclusion).
* The host directory's `.venv` is not mapped into the container's `/opt/venv`.

### CHORE-028: Audit Docker Build Caching and Layer Sizes
**Type:** Technical
**Description:** Perform QA verification to ensure the new Docker build process successfully utilizes BuildKit caching and produces sub-50MB final layers.
**Acceptance Criteria:**
* A dry run of `docker build --no-cache .` followed by `docker build .` demonstrates native `uv` caching.
* The output of `docker history` confirms the virtual environment layer size is within the sub-50MB threshold.

### SPIKE-019: Frontend/JS Infrastructure Optimization (Bun)
**Type:** Spike
**Description:** Draft a comprehensive implementation plan for replacing Node.js/npm with Bun for all JavaScript/TypeScript microservices and UI build pipelines.
**Acceptance Criteria:**
* Detail how to safely migrate `package.json` dependencies and build scripts from Node to Bun.
* Evaluate the feasibility and process of compiling the JS services into standalone executables (removing `node_modules` entirely from production).
* Address potential compatibility issues with our current testing framework.

### Phase 2: Memory & Tooling
### SPIKE-017: Vector Memory Database (MCP) Migration
**Type:** Spike
**Description:** Draft an implementation plan to formalize Wanda's memory indexing using `mcp-server-postgres` rather than a flat `MEMORY.md` file.
**Acceptance Criteria:**
* Output a detailed plan for deploying a dedicated `pgvector` container specifically for Swarm Memory.
* Define the data migration strategy from `MEMORY.md`.
* Define reliability mechanisms for Wanda's offline/dream cycles.

### SPIKE-020: Tool Discovery Automation (`mcp-server-discovery`)
**Type:** Spike
**Description:** Draft a plan to integrate `mcp-server-discovery` to automatically bridge local APIs, DBs, and ClawHub skills.
**Acceptance Criteria:**
* Detail the installation and configuration of the discovery server within our environment.
* Security Checkpoint (The Coulson Tollbooth): Implement a manual review/verification gate. The system must NEVER auto-activate unverified tools/MCPs without explicit Orchestrator/Secretary approval.

### Phase 3: Cognitive & Orchestration Upgrades
### SPIKE-016: Semantic Routing Architecture Plan
**Type:** Spike
**Description:** Draft an implementation plan for intercepting and routing Swarm Worker inference requests locally before they hit the cloud APIs.
**Acceptance Criteria:**
* Detail integration of a semantic router (e.g., `semantic-router` python library) into the FastAPI `swarm_worker.py` pipeline.
* Evaluate if the semantic router can natively perform intent/complexity classification. If it cannot, define the exact handoff mechanism to Jarvis for dynamic triage.
* Define environmental considerations for WSL2/Docker latency.

### SPIKE-021: Dynamic Context Loading (The Persona Toggle)
**Type:** Spike
**Description:** Modify the OpenClaw orchestration logic to conditionally load agent persona files based on the current ticket state.
**Acceptance Criteria:**
* Hard Rule Migration: Audit existing `SOUL.md` and `STYLE.md` files and outline moving any hard operational rules/safety constraints into `SKILL.md` or `IDENTITY.md` so they are never toggled off.
* Determine how to exclude `SOUL.md`/`STYLE.md` during execution (`BUILDING`, `TESTING`) and load them during planning (`REFINEMENT`, `RETROSPECTIVE`).

### Phase 4: Self-Optimization
### SPIKE-022: Agentic Self-Reflection & Role Optimization
**Type:** Spike
**Description:** Execute a training sequence where each agent leverages live web searches to research 2026 industry best practices for their specific roles.
**Acceptance Criteria:**
* Must be executed *after* Vector DB, Semantic Routing, and new models are fully operational.
* Agents must output a critical review of their current limitations.
* PROPOSAL ONLY: Agents must *propose* a modernized V2 of their configuration files. They are strictly forbidden from writing or overwriting the actual files to ensure no personality diversity or critical constraints are lost.
