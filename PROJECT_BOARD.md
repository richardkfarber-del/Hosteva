# Hosteva Project Board

> CURRENT_FOCUS_TARGET: FEAT-011, FEAT-012, FEAT-013, FEAT-014

## Active Sprint
**Batch Sprint Goal:** Florida V1 Foundation & Paywalled Gemini AI Integration
**Definition of Done (Strict Constraint):** Completion requires explicit final sign-off from Black Widow, Wasp, Falcon, and Hawkeye confirming functionality and monetization gates.

### > CURRENT_FOCUS_TARGET: BUG-008: SQLAlchemy Driver Prefix Crash
**Status:** TODO
**Description:** The application crashes on Render with a 503 error because SQLAlchemy defaults to loading `psycopg2` when the `postgresql://` connection prefix is used. We must update `app/database.py` to correctly map the connection string to `postgresql+psycopg://` to utilize the modern psycopg v3 driver installed during BUG-007.

**Acceptance Criteria:**
```gherkin
Feature: Update SQLAlchemy Driver Prefix (BUG-008)

  Scenario: Engineering (Data/Backend) Implementation
    Given the database driver has been migrated to psycopg v3
    And the application configures its database connection in "app/database.py"
    When the SQLAlchemy database engine is initialized
    Then the connection string prefix MUST be exactly "postgresql+psycopg://"
    And the application MUST connect to the PostgreSQL database without attempting to load the legacy "psycopg2" module.

  Scenario: Development (Frontend) Integration
    Given the connection string prefix has been updated
    When the application is deployed and started in the Render environment
    Then the application MUST successfully establish a database connection
    And the application MUST NOT crash with a "ModuleNotFoundError: No module named 'psycopg2'"
    And the application MUST resolve the previous 503 Render crash.
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
