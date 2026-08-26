# Hosteva — Milestone Roadmap & Sprints (GTM Launch Strategy Phase)

This document outlines our structured, 12-week three-phase GTM implementation and launch roadmap.

---

# Phase 1: Stabilization & Private Pilot (Weeks 1-4)

### Milestone Goal: Core Reliability & Pilot Fundraising

* **Objective:** Resolve immediate technical debt and launch the Founder Program to secure non-dilutive validation capital.  
* **Engineering Focus:**  
  - **Address Parameter Binding:** Resolve autocomplete address parameter loss on the `/wizard` route transition to ensure seamless geocoding.  
  - **Memory Migration:** Complete the pgvector vector memory database migrations and optimize SQLAlchemy queries.  
  - **Asynchronous Rewrites:** Execute Render deployment asyncio rewrites to ensure high concurrency under load.  
* **Commercial Focus:**  
  - **The Founder Program:** Recruit select pilot property owners, charging $5,000 for structural assessment and $15,000 for direct manual/AI compliance setup, providing non-dilutive development funding.

---

# Phase 2: Private Beta & Paywall Integration (Weeks 5-8)

### Milestone Goal: Paywall Scaffolding & AI Auditor Engine

* **Objective:** Integrate monetization structures and enable the core AI-powered document auditing systems.  
* **Engineering Focus:**  
  - **Stripe Billing Integration:** Implement the Stripe payment gateway mapping Free, Starter ($29/mo), Growth ($59/mo), and Enterprise ($149/mo) SaaS subscription tiers.  
  - **AI Document Auditor (OCR):** Build the FastAPI endpoint and background Celery tasks that send uploaded checklist files through Gemini 1.5 Pro to extract permit numbers and validate metadata.  
  - **Core Logic Binding:** Connect the underlying PostgreSQL models with the frontend dashboard viewport to render dynamic, real-time checklist updates rather than static mocks.

---

# Phase 3: Public Beta & Channel Launch (Weeks 9-12)

### Milestone Goal: Syndication, Unified inbox, & Portfolio Growth

* **Objective:** Deploy simple calendar syndication, roll out communication modules, and scale the property portfolio.  
* **Engineering Focus:**  
  - **Simplified Syndication (iCal Fallback):** Release the iCal-based import/export synchronization engine to block dates and sync schedules across Airbnb and Vrbo without direct API partnership barriers.  
  - **Unified AI Inbox:** Deploy the centralized communications inbox with Gemini-drafted guest response suggestions.  
* **Commercial Focus:**  
  - **Growth Outreach:** Initiate localized B2B marketing, sales campaigns, and direct outreach targeting regional Florida property management portfolios.

