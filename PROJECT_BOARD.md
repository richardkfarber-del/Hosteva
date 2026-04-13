# Sprint 4: Live Sync, AI Intelligence & Monetization
> CURRENT_FOCUS_TARGET

## Epic 4: Hosteva Core Engine Expansion
**Objective:** Enable live property sync from Airbnb/VRBO, integrate Gemini RAG for intelligent insights, and implement the Stripe paywall for premium AI features.

### FEAT-011 / Spike 301: Airbnb/VRBO Live Sync Implementation
**Domain:** Engineering / Development
**Feature:** OAuth & Listing Ingestion Sync

**Scenario:** Engineering (Data/Backend) Implementation
**Given** an infrastructure ready to handle external API connections
**When** the OAuth callback is triggered from Airbnb/VRBO
**Then** the backend must validate the authorization code
**And** securely store the access tokens in the database
**And** initiate the asynchronous Spike 301 ingestion job to pull listing data.

**Scenario:** Design (UI/UX) Implementation
**Given** the user is in the Integration Settings page
**When** the user views the Airbnb/VRBO connection options
**Then** the UI must present clear, branded OAuth connection buttons
**And** display a visual "Sync in Progress" indicator during the data ingestion phase.

**Scenario:** Development (Frontend) Integration
**Given** the user has clicked to connect an account
**When** the OAuth flow redirects back to the Hosteva dashboard
**Then** the frontend must capture the status and poll the backend for sync completion
**And** update the properties list dynamically without requiring a full page refresh.

### FEAT-012: Gemini RAG Infrastructure
**Domain:** Engineering / Data Science
**Feature:** Retrieval-Augmented Generation for STR Compliance

**Scenario:** Engineering (Data/Backend) Implementation
**Given** the application has ingested local Short-Term Rental compliance documents
**When** a compliance query is received via the API
**Then** the backend must perform a vector search using Gemini RAG to retrieve context chunks
**And** format the AI response with source document citations.

**Scenario:** Design (UI/UX) Implementation
**Given** the user is viewing the compliance insights module
**When** the AI is generating a response
**Then** the interface must show an intuitive loading state (e.g., typing indicator)
**And** clearly differentiate AI-generated insights from static data visually.

**Scenario:** Development (Frontend) Integration
**Given** the user submits a zoning or permit query
**When** the frontend calls the Gemini RAG endpoint
**Then** it must handle streaming or structured responses smoothly
**And** render citations as clickable links to the source documents.

### FEAT-013: AI Premium Paywall Integration (Stripe)
**Domain:** Development / Design
**Feature:** Stripe Monetization for Premium AI Features

**Scenario:** Engineering (Data/Backend) Implementation
**Given** Stripe webhooks are configured
**When** a successful payment event is received
**Then** the backend must update the user's subscription status to "Hosteva Premium"
**And** instantly grant API access to the RAG infrastructure routes.

**Scenario:** Design (UI/UX) Implementation
**Given** an un-subscribed user is on the platform
**When** they interact with the premium AI compliance insight module
**Then** the UI must render a locked state overlay
**And** provide a compelling call-to-action (CTA) explaining premium benefits.

**Scenario:** Development (Frontend) Integration
**Given** a user clicks the premium CTA
**When** the frontend triggers the checkout flow
**Then** it must seamlessly redirect the user to the Stripe Checkout session
**And** properly handle the success or cancellation redirect back to the app.

### BUG-001: Celery Removal & Background Tasks Refactoring
**Domain:** Engineering / Development
**Status:** **READY FOR EXECUTION**
**Description:** Refactor background task architecture to remove Celery dependency, migrating to a lightweight async queue as detailed in `planning/BUG-001_celery_removal.md`.

### BUG-002: Master Gate 1 Fixes
**Domain:** Engineering / Development
**Status:** **READY FOR EXECUTION**
**Description:** Implement comprehensive fixes identified during Master Gate 1 audit, as detailed in `planning/BUG-002_master_gate1_fixes.md`.

### BUG-003: OTA Router Import Fix
**Domain:** Engineering / Development
**Status:** **READY FOR EXECUTION**
**Description:** Resolve the missing OTA router import in `app/main.py` causing 404 errors on `/api/v1/integrations/ota` routes, as detailed in `planning/BUG-003_ota_router_import.md`.
