# Hosteva — Production Backlog (GTM Launch Strategy Phase)

This document details the granular, developer-ready backlog tickets for the 12-week GTM launch phase. Every ticket conforms to Hosteva's compliance-driven, asynchronous architecture and includes explicit technical execution steps, positive test criteria, and negative test criteria.

---

## Phase 1: Stabilization & Private Pilot (Weeks 1-4)

### HSV-101: Resolve `/wizard` Route Address Parameter Binding & Autocomplete State Preservation

- **User Story:** As a prospective host, I want my selected autocomplete address on the landing page to be preserved when I redirect to `/wizard`, so that I don't have to retype my address.  
- **Technical Implementation Details:**  
  - *Frontend:* In `src/routes/wizard.tsx` (or vanilla Javascript equivalent), implement a URL query parameter extractor on page load: `const queryParams = new URLSearchParams(window.location.search); const addressParam = queryParams.get('address');`.  
  - *Input Binding:* If the query parameter is present, decode the string, pre-populate the autocomplete input search field, and trigger the click event on the "Run Compliance Audit" button automatically.  
- **AI Verification Criteria:**  
  - **Positive Test:** Navigating to `/wizard?address=123+Main+St` in headful testing verifies that the address search field displays "123 Main St" and auto-triggers the compliance check skeleton.  
  - **Negative Test:** Navigating to `/wizard` with no query parameters renders an empty input search field, ready for input, without console errors.

### HSV-102: Migrate Vector Store Chunks to PostgreSQL `pgvector` & Optimize Asyncio Queries

- **User Story:** As an operator, I want semantic searches on municipal codes to resolve rapidly and run on our PostgreSQL production stack, so that I eliminate local file-locking delays.  
- **Technical Implementation Details:**  
  - *Database:* Set up the `pgvector` extension in the PostgreSQL schema migrations. Map the `ordinances` table to store embeddings: `embedding Column(Vector(1536))`.  
  - *FastAPI Asyncio:* Convert database lookups inside the FastAPI routers to use asynchronous query builders: `await db.execute(select(MunicipalCode).where(...))`.  
- **AI Verification Criteria:**  
  - **Positive Test:** Querying `/api/v1/compliance/search` triggers semantic vector searches in `pgvector` and returns matching municipal codes in under 150ms.  
  - **Negative Test:** Simulated vector indexing failures fallback gracefully to standard text searches, preventing 500 endpoint failures.

---

## Phase 2: Private Beta & Paywall Integration (Weeks 5-8)

### HSV-201: Implement Stripe Subscription Gateway & Webhook Listening Pipeline

- **User Story:** As a registered host, I want to subscribe to the Starter ($29/mo) or Growth ($59/mo) tiers and pay a $150 direct permit filing fee, so that I can unlock premium operations and automation.  
- **Technical Implementation Details:**  
  - *Backend:* Create `POST /api/v1/billing/checkout` which accepts tier selections or add-on parameters, initializes Stripe Checkout sessions, and returns checkout page links.  
  - *Webhooks:* Implement the endpoint `POST /api/v1/billing/webhooks` which listens for Stripe webhook events: `customer.subscription.created`, `invoice.payment_succeeded`, and `checkout.session.completed` to update the user's billing state.  
- **AI Verification Criteria:**  
  - **Positive Test:** Triggering a Stripe webhook containing a completed session payload updates the target user's model status to `ACTIVE` and unlocks subscription privileges.  
  - **Negative Test:** Attempting to trigger webhooks with malformed cryptographic headers returns a 400 Bad Request, preventing fraud.

### HSV-202: Deploy Gemini 1.5 Pro AI Document Auditor Queue

- **User Story:** As a host, I want to upload document files to my compliance checklist items (HOA, lease, DBPR, or tax docs) and have the system automatically audit the documents via AI, so that I know if I have what I need.  
- **Technical Implementation Details:**  
  - *Backend:* Implement FastAPI route `POST /api/v1/compliance/audit` which accepts uploaded files (PDF, PNG, JPG) and enqueues a Celery task.  
  - *Background Worker:* In `app/tasks/audit.py`, implement Celery task `tasks.process_document_ocr` that:  
    1. Sends the uploaded document to Gemini 1.5 Pro via the SDK.  
    2. Uses a structured system prompt instructing Gemini to extract name, address, license number, and expiration date in JSON.  
    3. Compares results with the property record, updating status to `APPROVED` or `REJECTED` based on matches.  
- **AI Verification Criteria:**  
  - **Positive Test:** Uploading a valid Florida DBPR license PDF updates compliance status to `APPROVED` and records extracted parameters in the checklist metadata.  
  - **Negative Test:** Uploading an invalid, empty, or unreadable document transitions status to `REJECTED` and populates verification notes with specific instructions (e.g. "Address Mismatch").

---

## Phase 3: Public Beta & Channel Launch (Weeks 9-12)

### HSV-301: Build iCal Import/Export Background Sync Engine for Airbnb/Vrbo

- **User Story:** As an active host, I want my Airbnb and Vrbo reservation calendars synchronized automatically using standard iCal feeds, so that I prevent booking conflicts without direct API partnership overhead.  
- **Technical Implementation Details:**  
  - *Worker Tasks:* In `app/tasks/calendar.py`, implement Celery task `tasks.sync_ical_calendars` that:  
    1. Downloads the active `.ics` files from the property's registered Airbnb and Vrbo URLs.  
    2. Parses the dates using `icalendar`, registers reservation records, and blocks dates.  
    3. Exports a unified, token-secured Hosteva `.ics` feed on a public endpoint for OTAs to ingest.  
- **AI Verification Criteria:**  
  - **Positive Test:** Executing the calendar sync task manually downloads mock `.ics` calendars, blocks dates, and exports a valid Hosteva `.ics` file containing consolidated blocks.  
  - **Negative Test:** Malformed, corrupt, or offline iCal import links raise warnings and skip execution, preserving existing calendar states.

### HSV-302: Implement Unified AI Inbox UI & Message Draft Auto-Generator

- **User Story:** As a host, I want all guest messages consolidated in a unified inbox with AI-generated draft responses matching my house rules, so that I can communicate with guests instantly.  
- **Technical Implementation Details:**  
  - *Frontend:* Create `src/components/operations/UnifiedInbox.tsx`. Render a clean, dual-column chat viewport. Left column displays thread summaries. Left column displays thread summaries. Right column shows the active thread logs, an AI-suggested draft text area, and an "Approve and Send" button.  
  - *Backend:* Implement FastAPI route `GET /api/v1/operations/messages` and `POST /api/v1/operations/messages/:id/reply`.  
  - *AI Generator:* Implement an async helper service `app/services/chat_ai.py` that queries Gemini 1.5 Pro on receipt of a guest message. Retrieve adjacent host house rules from SQLite, pass them as constraints, and instruct the model to draft an appropriate response.  
- **AI Verification Criteria:**  
  - **Positive Test:** Ingesting a guest query triggers Gemini, which auto-generates a contextual draft based on house rules, ready for approval.  
  - **Negative Test:** Network/AI service failures display a graceful placeholder error banner, enabling manual typing inputs.

