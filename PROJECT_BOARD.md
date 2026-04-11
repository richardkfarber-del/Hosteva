# Hosteva Project Board

> CURRENT_FOCUS_TARGET: FEAT-011, FEAT-012, FEAT-013, FEAT-014

## Active Sprint
**Batch Sprint Goal:** Florida V1 Foundation & Paywalled Gemini AI Integration
**Definition of Done (Strict Constraint):** Completion requires explicit final sign-off from Black Widow, Wasp, Falcon, and Hawkeye confirming functionality and monetization gates.

### > CURRENT_FOCUS_TARGET: BUG-004: Missing get_db in app.database
**Status:** TODO
**Description:** The `app/database.py` file is missing the `get_db()` generator function. Other routers are failing to import it, causing a deployment crash. We must append the `get_db` function back into `app/database.py`.

**Acceptance Criteria:**
```gherkin
Feature: Restore get_db Dependency (BUG-004)

  Scenario: [Engineering] Restore the get_db generator function
    Given the `app/database.py` file has been migrated to Postgres
    And the `get_db()` generator function is missing from the file
    When the developer appends the `get_db()` function that yields a database session
    Then legacy routers like `app/routers/zoning.py` will successfully import the function
    And the application will boot without raising an ImportError

  Scenario: [Development] Verify application boot stability
    Given the `get_db()` function is restored in `app/database.py`
    When the application is deployed and initialized
    Then the application starts successfully without crashing
    And endpoints relying on the database session execute properly
```

## Backlog
### > CURRENT_FOCUS_TARGET: FEAT-014: Progressive Web App Core Migration
**Status:** TODO
**Description:** Migrate frontend from Jinja2/Tailwind CDN to a modern Vite build pipeline with Workbox Service Workers and web manifest.

**Acceptance Criteria:**
```gherkin
Feature: Progressive Web App (PWA) Core Migration (FEAT-014)

  Scenario: Engineering (Data/Backend) Implementation
    Given the Hosteva application infrastructure currently utilizes Jinja2 templates and a Tailwind CDN
    When the system build pipeline executes the new Vite configuration with Workbox Service Worker integration
    Then the system pipeline shall successfully generate optimized static assets, Service Worker caches, and a valid web manifest file

  Scenario: Design (UI/UX) Implementation
    Given the Hosteva web interface is rendered on a supported mobile or desktop browser
    When the system user views the application and triggers the "Add to Home Screen" installation prompt
    Then the system interface must display the standardized PWA application icon, splash screen, and native-like standalone window parameters

  Scenario: Development (Frontend) Integration
    Given the system user is accessing the Hosteva frontend application
    When the system user loses network connectivity and attempts to navigate core views
    Then the frontend application must successfully retrieve offline assets via the Workbox Service Worker to maintain core UI functionality
```


### BUG-002: Clean up Duplicate JS in FEAT-011
**Status:** DONE
**Description:** The `app/templates/ordinance_directory.html` file contains duplicated fetch logic (an async/await block and a Promise chain block targeting two different element IDs). The UI/UX lead must use `aider` to refactor the file to contain exactly one standardized JavaScript fetch block mapping to the backend endpoints.

**Acceptance Criteria:**
```gherkin
Feature: UI Cleanup for FEAT-011 (BUG-002)

  Scenario: Development (Frontend) Integration
    Given the ordinance_directory.html template contains duplicate fetch scripts
    When the system user refactors the frontend file
    Then the template must contain exactly one JavaScript fetch block targeting the correct DOM container
```
