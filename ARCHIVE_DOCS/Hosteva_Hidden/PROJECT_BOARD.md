# Sprint 11

> CURRENT_FOCUS_TARGET: Regression Sprint (UI/UX Audit & Bug Fixes)

## Sprint Goals
1. **Regression:** Execute a comprehensive UI/UX Audit and resolve outstanding bugs before advancing. (Regression Sprint - Absolute Sole Focus)
2. **Infrastructure (Paused):** Implement PostgreSQL-Backed Background Queue as a hard prerequisite for the dashboard. (FEAT-018)

---

## REGRESS-001: UI/UX Audit Master Ticket
**Status:** In Progress (Active Sprint Focus)
**Description:** Comprehensive audit of all UI components and user experience flows across the application to identify visual regressions, layout issues, and broken template logic.
### Acceptance Criteria:
- [ ] **Wasp (UI/UX):** Audit all core user flows and document visual anomalies or design token violations.
- [ ] **Wasp (UI/UX):** Verify responsiveness across mobile, tablet, and desktop breakpoints.
- [ ] **Captain America (QA):** Validate all identified issues are triaged into specific BUG tickets.

## BUG-001: dashboard.html Template Literal Leak
**Status:** To Do
**Description:** Template literal leakage on the `dashboard.html` page where raw JavaScript is rendering as plain text underneath the Geospatial Parcel Map.
### Acceptance Criteria:
- [ ] **Wasp / Iron Man:** Identify the unescaped or improperly formatted template literal in the dashboard view/template.
- [ ] **Wasp / Iron Man:** Fix the syntax so the script executes correctly or is properly abstracted without leaking raw JS into the DOM.
- [ ] **Captain America (QA):** Verify the raw JS text is no longer visible under the Geospatial Parcel Map and the map continues to function normally.

## BUG-002: Persistent Broken Logo
**Status:** To Do
**Description:** The application logo fails to load consistently across views, resulting in a broken image icon.
### Acceptance Criteria:
- [ ] **Wasp (UI/UX):** Ensure the correct asset path is used for the logo across all templates.
- [ ] **Captain America (QA):** Verify the logo renders correctly on all major views.

## BUG-003: CSS Duplication in /dashboard
**Status:** To Do
**Description:** Duplicate CSS rules and redundant styling are loading in the `/dashboard` route, potentially causing conflicts or bloating page weight.
### Acceptance Criteria:
- [ ] **Wasp (UI/UX):** Audit and remove duplicate CSS classes or redundant stylesheets affecting the dashboard.
- [ ] **Captain America (QA):** Verify the dashboard layout remains visually correct and the CSS payload size is reduced.

## BUG-004: Silent Failure on Empty Form Submit (/wizard)
**Status:** To Do
**Description:** Submitting the form on `/wizard` without filling out required fields fails silently instead of displaying validation errors.
### Acceptance Criteria:
- [ ] **Iron Man / Wasp:** Implement frontend form validation or properly surface backend validation errors on the `/wizard` UI.
- [ ] **Captain America (QA):** Verify that attempting to submit an empty form displays clear error messages and prevents submission.

---

## FEAT-018: PostgreSQL-Backed Background Queue
**Status:** Paused (Preempted by Regression Sprint)
**Description:** Implement the lightweight async queue leveraging the existing Render DB to replace Celery (which was removed in Sprint 10), following SPIKE_queue_persistence findings. Hard prerequisite for FEAT-016.

### Acceptance Criteria:
- [ ] **Vision (Data):** Create the necessary PostgreSQL tables for job tracking (`jobs` table).
- [ ] **Iron Man (Backend):** Implement async worker logic utilizing `SELECT ... FOR UPDATE SKIP LOCKED` or the `Procrastinate` library.
- [ ] **Iron Man (Backend):** Create the `/api/v1/queue/jobs` endpoints (POST enqueue, GET status) as defined in the spike contract.
- [ ] **Captain America (QA):** Verify jobs can be enqueued, executed asynchronously without OOM or deadlocks, and queried for status.

---

# Future Backlog

## FEAT-016: Final Dashboard Integration & User Analytics
**Status:** Paused (Blocked by FEAT-018)
**Description:** The core Hosteva engine is functionally complete. This epic focuses on final dashboard integration and user analytics. Paused pending FEAT-018 to resolve Hulk's architectural flag.

### API Contract (BFF JSON Payload)
`GET /api/v1/dashboard/overview`
```json
{
  "user_id": "string",
  "subscription_tier": "string",
  "recent_queries": [
    {
      "query_id": "string",
      "timestamp": "iso8601",
      "summary": "string"
    }
  ],
  "analytics": {
    "total_queries": 0,
    "quota_remaining": 0
  }
}
```

### Acceptance Criteria:
- [ ] **Given** an authenticated user navigates to the dashboard, **When** the dashboard initializes, **Then** the application retrieves the user's active Subscription Tier and RAG query history via the `GET /api/v1/dashboard/overview` endpoint.
- [ ] **Given** the BFF endpoint responds with the agreed JSON payload, **When** the data is received by the frontend, **Then** the UI displays the `subscription_tier`, `analytics.quota_remaining`, and a list of `recent_queries`.

## FEAT-017: RAG Prompt Injection Middleware
**Status:** Backlog
**Description:** Implement the prompt injection middleware architecture determined in SPIKE-002_rag_security.

### Acceptance Criteria:
- [ ] **Iron Man (Backend):** Create middleware to intercept `/api/v1/rag/*` routes.
- [ ] **Iron Man (Backend):** Apply heuristic checks (regex for jailbreaks/DAN, length limits).
- [ ] **Iron Man (Backend):** Reject malicious prompts with HTTP 400 and `error_code: PROMPT_INJECTION_BLOCKED`.
- [ ] **Captain America (QA):** Verify middleware blocks known prompt injection payloads and permits standard real-estate queries.

## FEAT-019: Authentication Flow & Login Route
**Status:** Backlog
**Description:** Implement the missing `/login` route and the complete user authentication flow. (Originally reported as a bug, but identified as an unbuilt feature).
### Acceptance Criteria:
- [ ] **Given** an unauthenticated user navigates to `/login`, **When** the page loads, **Then** the application displays a secure login interface.
- [ ] **Given** a user provides valid credentials, **When** the backend processes the login request, **Then** a secure session is established and the user is redirected to the dashboard.
- [ ] **Given** an authenticated user initiates a logout, **When** the request is processed, **Then** the session is securely terminated and the user is redirected to the login interface.

## FEAT-020: Integrations Route & Wiring
**Status:** Backlog
**Description:** Wire up the existing integrations template to a live `/integrations` route and backend endpoints. (Originally reported as a bug).
### Acceptance Criteria:
- [ ] **Iron Man (Backend):** Establish backend routing and data contracts for the integrations view.
- [ ] **Wasp (UI/UX):** Connect the existing template to the active `/integrations` route.
- [ ] **Captain America (QA):** Verify the integrations view loads and displays correctly when navigated to.

