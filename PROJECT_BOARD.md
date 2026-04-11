# Hosteva Project Board

> CURRENT_FOCUS_TARGET: FEAT-011, FEAT-012, FEAT-013, FEAT-014

## Active Sprint

**Batch Sprint Goal:** Florida V1 Foundation & Paywalled Gemini AI Integration
**Definition of Done (Strict Constraint):** Completion requires explicit final sign-off from Black Widow, Wasp, Falcon, and Hawkeye confirming functionality and monetization gates.

### > CURRENT_FOCUS_TARGET: FEAT-011: Florida Ordinance Data Pipeline
**Status:** TODO
**Description:** Build the ingestion and normalization pipeline to construct a database of Florida state and municipal STR ordinances.

**Acceptance Criteria:**
```gherkin
Feature: Florida Ordinance Data Pipeline (FEAT-011)

  Scenario: System ingests and normalizes Florida municipal ordinances
    Given the data pipeline is active
    When the system processes Florida municipal STR regulations
    Then the system shall ingest the data into a centralized database
    And the system shall normalize the regulations into queryable compliance rules
```

### > CURRENT_FOCUS_TARGET: FEAT-012: Gemini RAG Infrastructure
**Status:** TODO
**Description:** Build the Retrieval-Augmented Generation (RAG) infrastructure to feed the Florida ordinance database into the Gemini LLM context window.

**Acceptance Criteria:**
```gherkin
Feature: Gemini RAG Infrastructure (FEAT-012)

  Scenario: Engineering (Data/Backend) Implementation
    Given the backend system has ingested a new set of compliance documents
    When the system processes the documents through the embedding pipeline
    Then the engineering infrastructure must store the resulting vectors in the secure vector database
    And the system must retrieve the top-K relevant chunks within 500ms when a query is executed

  Scenario: Design (UI/UX) Implementation
    Given the Gemini RAG query is processing
    When the user waits for the generated response
    Then the design implementation must render a localized skeleton loader or streaming text animation
    And the UI must clearly attribute the sourced documents in a collapsible citation component below the response

  Scenario: Development (Frontend) Integration
    Given a user submits a natural language query regarding compliance regulations
    When the client application sends the query payload to the RAG endpoint
    Then the development layer must construct the prompt appending the retrieved vector context
    And the system must return the Gemini-generated response mapped to the standardized JSON schema
```

### > CURRENT_FOCUS_TARGET: FEAT-013: AI Premium Paywall Integration
**Status:** TODO
**Description:** Implement a strict monetization gate (e.g., Stripe) that blocks access to Gemini AI features for free-tier users.

**Acceptance Criteria:**
```gherkin
Feature: AI Premium Paywall Integration (FEAT-013)

  Scenario: Engineering (Data/Backend) Implementation
    Given a user attempts to access the Gemini RAG endpoints
    When the backend receives the API request
    Then the engineering layer must validate the user's current Stripe subscription token
    And the system must reject the request with a 403 Forbidden status code if the active premium entitlement is missing

  Scenario: Design (UI/UX) Implementation
    Given the user is browsing the dashboard on a basic tier
    When the design components render the premium AI features
    Then the UI must display a lock icon adjacent to the feature titles
    And the system must present a visually distinct "Upgrade to Premium" banner that highlights the benefits of the AI toolset

  Scenario: Development (Frontend) Integration
    Given an authenticated user with a basic (free) account state
    When the user clicks on a premium-locked AI feature component
    Then the development layer must intercept the routing event
    And the application must redirect the user to the subscription checkout flow without executing the underlying feature logic
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
