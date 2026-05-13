# Sprint 3: The Value Delivery - Backlog

### [EMERGENCY BUG] Missing Dashboard Navigation
**Current Behavior:** The Dashboard navigation button is completely missing from the UI on the root and `/wizard` endpoints.
**Expected Behavior:** The web application must contain a visible and functional navigation link or button on the root (`/`) and wizard (`/wizard`) pages that successfully routes the user to the `/dashboard` endpoint.

[FEEDBACK - Iron Man]
**Diagnosis:** The live server is returning a static file response for the root route instead of processing the Jinja2 template. In `app/main.py`, the `@app.get("/")` route currently returns `FileResponse("templates/landing.html")`. Because it is served as a static file, Jinja2 template parsing is skipped, causing `href="{{ url_for('dashboard') }}"` to be rendered literally on the client side, leading to a broken `/%7B%7B%20url_for('dashboard')%20%7D%7D` route (404 error).
**Backend Fix for The Hulk:** Update the `@app.get("/")` endpoint in `app/main.py` to return a `TemplateResponse` using the `Jinja2Templates` instance. 
Change it to:
```python
@app.get("/", include_in_schema=False)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="landing.html", 
        context={"request": request}
    )
```


[FEEDBACK - Iron Man]
**Diagnosis:** Hawkeye's UAT FAILED. The live server is returning an Internal Server Error because the Jinja2 engine encountered `{{ url_for('dashboard') }}` in `landing.html` but threw `starlette.routing.NoMatchFound: No route exists for name "dashboard" and params ""`. In FastAPI/Starlette, `url_for` looks up routes by their `name` parameter or their function name. The dashboard route in `app/main.py` is defined as `@app.get('/dashboard')` with the function name `read_dashboard`, so `url_for('dashboard')` fails to match it.
**Backend Fix for The Hulk:** Update the dashboard route in `app/main.py` to explicitly name the route "dashboard".
Change it to:
```python
@app.get('/dashboard', name="dashboard")
def read_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={"request": request, "google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY", ""), "active_page": "dashboard"}
    )
```

## MANDATORY SPIKES FIRST

### Ticket: TCK-301 [SPIKE] Research & Define Backend Architecture for Airbnb & VRBO Integrations
**Description:**
Investigate the official API documentation for Airbnb and VRBO to support automated listing generation and posting. Define the database schemas and asynchronous mechanics required to securely manage the integration.
*   Research authentication flows (OAuth2, Bearer tokens, Partner API access).
*   Define the OAuth token storage schema to securely store and refresh user credentials for third-party platforms.
*   Define a 1-to-many `property_listings` database schema to track external listings (e.g., `property_id`, `platform_name`, `external_listing_id`, `status`).
*   Determine async task queue mechanics (e.g., Celery/Redis) to handle long-running API calls, retries, and rate limits.
*   Identify endpoints for creating and updating property listings, including required payloads for pricing, photos, and availability.

**The API Contract Mandate:**
The research must define the complete required JSON payload contracts for the endpoints, including pricing, photos, and availability. Complex payloads must be written to /workspace/Hosteva/state.json per LOBSTER protocol.

## User Stories

### Ticket: TCK-302 Feature: State DBPR Form Auto-Fill
**Description:**
Auto-fill the required state DBPR forms using the property data collected during onboarding to streamline compliance.

**Gherkin Acceptance Criteria:**
```gherkin
Feature: DBPR Form Auto-Fill

  Scenario: The system automatically populates the state DBPR form
    Given a property profile has been successfully saved with valid address and ownership details
    When the system initiates the DBPR compliance application process
    Then the system shall map the database fields to the corresponding DBPR form inputs
    And the system shall generate a populated DBPR form document
    And the system shall flag any missing mandatory fields for user review
    And the system shall record the compliance application status and document URI in the database
```

### Ticket: TCK-303 Feature: Search-Safe Listing Generator & Async Post to Airbnb/VRBO
**Description:**
Generate SEO-optimized, search-safe listing descriptions and automatically publish the property to Airbnb and VRBO via an asynchronous task queue. Securely utilize stored OAuth tokens and track the listing statuses in a 1-to-many relationship.

**Gherkin Acceptance Criteria:**
```gherkin
Feature: Listing Generation and Asynchronous Platform Integration

  Scenario: The system generates a listing description and asynchronously posts it to target platforms
    Given the property details are complete and compliance verification is approved
    And the system holds valid OAuth tokens for the target platforms in the secure token storage schema
    When the system triggers the listing generation module
    Then the system shall generate a search-safe, compliance-approved listing description
    And the system shall assemble the required comprehensive JSON payloads including pricing, photos, and availability
    And the system shall dispatch an asynchronous background task to transmit the payloads to the Airbnb and VRBO APIs
    And the asynchronous task shall handle rate limiting, retries, and token refresh logic
    And the system shall record the returned external listing IDs and statuses in the 1-to-many property_listings schema upon task completion
```

## Definition of Done (DoD)
*   **Testing:** Automated `pytest` suites are implemented and passing for all new endpoints, payload builders, and background workers.
*   **QA:** Local and production-parity testing successfully completed by QA.
*   **Contracts:** API contracts for third-party integrations are explicitly documented and adhered to.
*   **Architecture:** Async queues, OAuth schemas, and 1-to-many listing schemas are deployed and verified.
*   **Formatting:** Code meets LOBSTER formatting rules.
*   **UAT:** Human UAT verification of the Dashboard navigation flow.

[APPROVED - Vision]

[APPROVED - Iron Man]
**Instructions for Wasp (UI/Routing Fix):**
1. Target the global Navigation Shell (`templates/base.html`).
2. Locate the existing responsive navigation container (the list or div handling the hamburger menu collapse for mobile).
3. Inject the link using Flask routing: `<a href="{{ url_for('dashboard') }}" class="[match_existing_nav_classes]">Dashboard</a>`.
4. Ensure the link is placed *inside* the mobile-responsive collapse wrapper so it does not break the viewport on small screens (preserving Sprint 1 mobile layouts).
5. If `landing.html` does not inherit `base.html`'s navbar, replicate the responsive injection there.

[SEALED - Captain America]
\n[APPROVED - Vision] No database or schema changes required for UI navigation link.
\n[SEALED - Captain America]

[FEEDBACK - Iron Man]
**Diagnosis:** The dashboard UI route physically exists directly in `app/main.py` at line 62 as `@app.get('/dashboard', name="dashboard")`. It is NOT imported via `app.include_router(dashboard_api.router)`. The reason UAT continues to fail with `NoMatchFound` is because Hawkeye's `run_uat_regression.py` script executes tests against the live production environment (`https://hosteva.onrender.com`), but the recent codebase fix adding `name="dashboard"` has not yet been deployed to Render. Locally, the application resolves `url_for('dashboard')` perfectly and returns a 200 OK.
**Backend Fix for The Hulk:** No further code changes are needed in `main.py` or `dashboard_api.py`. The Hulk simply needs to trigger a deployment of the `main` branch to Render so the production server picks up the updated `@app.get('/dashboard', name="dashboard")` route. Once the live server is updated, the Jinja2 template will successfully resolve the `dashboard` URL and the UAT regression script will pass.
