# Hosteva Project Board

## Current Focus Target
Sprint 15: FEAT-018 (PostgreSQL-Backed Background Queue)

## Active Tickets

### TICKET-01: Vision (Data) - Create `jobs` tracking table in PostgreSQL
**Description:** Establish the foundational data schema for the background queue.
**Acceptance Criteria:**
* Given a database schema initialization process,
* When the database migrations are executed,
* Then a `jobs` table is successfully created with columns for ID, payload, state, and timestamp tracking.

### TICKET-02: Iron Man (Backend) - Implement async worker logic utilizing `SELECT ... FOR UPDATE SKIP LOCKED`
**Description:** Build the asynchronous worker execution layer to process queued jobs without lock contention.
**Acceptance Criteria:**
* Given an active pool of background worker processes,
* When the workers concurrently poll the `jobs` table for pending tasks,
* Then the system utilizes `SELECT ... FOR UPDATE SKIP LOCKED` to exclusively acquire and process distinct jobs without deadlocking.

### TICKET-03: Iron Man (Backend) - Create `/api/v1/queue/jobs` endpoints (POST enqueue, GET status)
**Description:** Expose the queue functionality to client applications via REST API.
**Acceptance Criteria:**
* Given an authorized client system,
* When a POST request is submitted to `/api/v1/queue/jobs` with a valid payload,
* Then the job is enqueued in the database and a unique tracking ID is returned to the client.
* Given an existing job in the queue,
* When a GET request is submitted to `/api/v1/queue/jobs/{id}`,
* Then the current execution status and payload of that job are returned to the client.

## Backlog
*None*

## Completed
- [x] BUG-001: JS Leak on Dashboard (Verified)
- [x] BUG-002: Broken Logo (Verified)
- [x] BUG-003: CSS Duplication (Verified)
- [x] BUG-004: Silent Form Failure on `/wizard` (Verified)

## Next Action Upon Wake
NEXT_ACTION_UPON_RESTART: Swarm agents to begin processing TICKET-01, TICKET-02, and TICKET-03 for Sprint 15.