# SPRINT BACKLOG

## BUG-004: Render 500 Error
**Type:** Bug
**Location:** `app/main.py`
**Expected Behavior:** The application must successfully boot on Render without throwing a 500 Internal Server Error, correctly parsing all environment variables and syntax.

## BUG-006: Stripe Webhook Database Logic Failure
**Type:** Bug
**Location:** `app/routers/stripe.py`
**Expected Behavior:** The Stripe webhook must execute the database logic to activate a user's subscription upon a successful payment event, rather than bypassing it via commented-out code.

## BUG-001: Dashboard Template Literal Leak
**Type:** Bug
**Location:** `templates/dashboard.html`
**Expected Behavior:** The map UI must render cleanly without any raw JavaScript template literals leaking into the visible DOM.

## BUG-005: UAT False Positives
**Type:** Bug
**Location:** `tests/uat_live_pricing.py`
**Expected Behavior:** The UAT script must correctly fail when live pricing data does not match the expected payload, eliminating all false positive assertions.

## BUG-003: Dashboard CSS Duplication
**Type:** Bug
**Location:** `templates/dashboard.html`
**Expected Behavior:** The dashboard must utilize a single, consolidated CSS file or block without duplicate style declarations causing visual conflicts.

## FEAT-019: Authentication Flow & Login Route
**Type:** User Story
**Acceptance Criteria:**
- Given a user is unauthenticated, When the user navigates to `/login`, Then the system must display the login form.
- Given a user submits valid credentials, When the system processes the request, Then the system must issue a session token and redirect to the dashboard.

## FEAT-017: RAG Prompt Injection Middleware
**Type:** Tech Ticket
**Acceptance Criteria:**
- Implement middleware to intercept all real-estate queries.
- Sanitize inputs to prevent system prompt overrides.
- Log flagged injection attempts to the security audit table.

## FEAT-020: Integrations Route & Wiring
**Type:** User Story
**Acceptance Criteria:**
- Given a user is on the dashboard, When the user clicks "Integrations", Then the system must route them to the `/integrations` view.
- Given a user is on the integrations view, When the user views the page, Then the system must display their active 3rd-party connections.
