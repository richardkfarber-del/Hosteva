# Hosteva Project Board

> CURRENT_FOCUS_TARGET: FEAT-011, FEAT-012, FEAT-013, FEAT-014

## Active Sprint
**Batch Sprint Goal:** Florida V1 Foundation & Paywalled Gemini AI Integration
**Definition of Done (Strict Constraint):** Completion requires explicit final sign-off from Black Widow, Wasp, Falcon, and Hawkeye confirming functionality and monetization gates.

### BUG-003: Render PostgreSQL Dependency Crash
**Status:** DONE
**Description:** The `Dockerfile` uses `python:3.12-slim` which lacks the C-compilers (`libpq-dev`, `gcc`) required to install `psycopg2`. The build fails, crashing the gunicorn workers. We must update the Dockerfile to `RUN apt-get update && apt-get install -y libpq-dev gcc` before `pip install`.

**Acceptance Criteria:**
```gherkin
Feature: Render PostgreSQL Dependency Fix (BUG-003)

  Scenario: Engineering (Data/Backend) Implementation
    Given the application uses the python:3.12-slim Docker base image
    When the image build process executes
    Then the Dockerfile must run apt-get update && apt-get install -y libpq-dev gcc before executing pip install
    And the psycopg2 package must compile and install successfully without missing C-compiler errors

  Scenario: Development (Frontend) Integration
    Given the updated Docker container is built and deployed to Render
    When the gunicorn workers initialize
    Then the application must successfully establish a connection to the PostgreSQL database
    And the web application must load seamlessly without throwing 500 Internal Server Errors related to database adapter failures

  Scenario: Design (UI/UX) Implementation
    Given this is a backend infrastructure bug
    When the user interacts with the UI
    Then there are no visual or design changes required
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
