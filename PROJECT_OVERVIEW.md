# Hosteva Project Overview

Hosteva is a premium Short-Term Rental (STR) Zoning and Compliance Platform designed to help property hosts navigate local municipal codes, HOA regulations, and platform-specific listing requirements. By binding real-time geocoding, AI-driven ordinance audits, and document validation services, Hosteva automates compliance management from onboarding to listing.

---

## 1. Tech Stack

### Backend
* **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
* **Database Toolkit & ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) & [Alembic](https://alembic.bygenius.org/) for migrations.
* **Background Worker**: [Celery](https://docs.celeryq.dev/) with [Redis](https://redis.io/) / AMQP.
* **Security & Auth**: [python-jose](https://github.com/mpdavis/python-jose) for JWT token generation and [bcrypt](https://github.com/pyca/bcrypt/) for secure password hashing.
* **JSON Validation**: [Pydantic V2](https://docs.pydantic.dev/) for strict API request/response schema parsing.

### Frontend
* **Core**: Semantic HTML5, Vanilla CSS3, Javascript (ES6+).
* **Styling**: Tailwind CSS (loaded in templates) + custom layouts.
* **Maps**: [Leaflet.js](https://leafletjs.com/) for interactive zoning parcel rendering.
* **Utilities**: [DOMPurify](https://github.com/cure53/DOMPurify) for security against XSS.

### AI & Integrations
* **GenAI / Vision API**: Google Gemini API (1.5 Pro) for structural audits, room scanning, and covenant rules discovery.
* **Geocoding & Street View**: Google Maps API, Google Street View API, and Google Places API.
* **Payment Processing**: Stripe API (Subscriptions, paywalls, and webhooks).
* **OTA Connection**: Mapped Airbnb & VRBO mock API endpoints for listing details synchronization.

---

## 2. Features Enabled

### A. Onboarding & Imagery Onboarding
* **Jurisdiction-Aware Geocoding**: Resolves raw address strings into city, county, and state components using the Google Maps Geocoding API to match county-level jurisdictional rules.
* **Street View Visual Verification**: Dynamically queries Google Street View metadata, downloads street-level imagery server-side, and associates it with the property card, falling back to Google Places photos or default house graphics.
* **Eligibility Pre-Validation**: Gated onboarding wizard modal `/wizard` checks zoning allowance and stay restrictions before database persistence.

### B. Dynamic Compliance Engine
* **Automated Zoning Audits**: Queries municipal database rules and uses Gemini 1.5 Pro to determine zoning compliance, stay limits, tax requirements, and needed permits.
* **HOA Covenants OCR**: Scans uploaded HOA/lease documents using OCR and prompts Gemini to extract rental constraints.
* **Document Audit Verification**: Handles uploaded permit registrations, tax certificates, and licenses, running automatic status checks (`PENDING`, `APPROVED`, `REJECTED`).
* **Zoning Compliance Alerts**: Sends automated email alerts via `dispatch_email_alert` when property zoning status transitions into a violation.

### C. Dashboard & Listing Optimizations
* **Interactive Parcel Map**: Renders property locations color-coded by zoning compliance status using Leaflet.js.
* **Dynamic Compliance Score**: Recalculates overall property health scores dynamically based on the ratio of completed checklist tasks.
* **Baseline Neutral Metrics**: Resets newly registered listings to a neutral starting point (`0%` Occupancy, `N/A` Rating, `$0.00` Revenue, and `Awaiting Audit` badges) to eliminate hardcoded mocks.
* **OTA Sync & Description Optimizer**: Downloads OTA listing content, scans descriptions against regional stay limits/permit codes, and suggests optimized compliance texts.
* **Permit Package Generator**: Auto-fills local county permit application forms and aggregates documentation checklists.

---

## 3. Database Architecture & Schema Map

Hosteva uses PostgreSQL (with SQLite for testing) mapping the following key entities:
* **Host**: User credential profiles, subscription references, and properties.
* **Property**: Contains addresses, geocoded metadata, property type, street view URL, and serialized rules configuration.
* **MunicipalCode**: Stores stay restriction rules, tax rates, required permits, and county-specific rules.
* **HOARule**: Keeps track of parsed HOA lease conditions.
* **PropertyCompliance**: Records the intersection between a property and its local municipal ordinances.
* **Ordinance**: Stores text definitions with Vector embeddings for semantic search.
* **Subscription**: Keeps track of Stripe customer records and host tier statuses.
