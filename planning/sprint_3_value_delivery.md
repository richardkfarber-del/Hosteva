# Sprint 3: The Value Delivery - Backlog

### [EMERGENCY BUG] Missing Dashboard Navigation
**Current Behavior:** The Dashboard navigation button is completely missing from the UI on the root and `/wizard` endpoints.
**Expected Behavior:** The web application must contain a visible and functional navigation link or button on the root (`/`) and wizard (`/wizard`) pages that successfully routes the user to the `/dashboard` endpoint.

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
