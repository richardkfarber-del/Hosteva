# Hosteva — Milestone Roadmap & Sprints (Phase III: Multi-State GTM & AI Agentic Launch)

This document outlines our structured, 12-week four-sprint development and launch roadmap to implement GTM multi-state database scaling, central dashboard document checklists, on-demand AI scraping agents, and PDF form filling.

---

# Sprint 34: 10-State Database Scaling & Marketing Copy (Weeks 1-3)

### Epic: Database Seeding & Brand Overhaul

* **Milestone Goals:** Migrate existing schemas to handle multi-state address geocoding, seed the complete 10-state rules database, and update UI verbiage.  
* **User Stories:**  
  - *As a host,* I want to register properties in FL, CA, TX, NY, CO, HI, GA, NC, TN, and AZ, so that I can audit listings in the top vacation rental markets.  
  - *As an investor,* I want the landing page and subscription modals to clearly advertise that Hosteva covers these 10 states, so that I trust the platform's authority.  
* **Technical Dependencies:** `Hosteva Jurisdictional Rules DB (Complete)` CSV seeding, updated geocoding city/county parsing algorithms.  
* **Verification Criteria:** Seed script successfully populates over 1,500 municipal code records across 10 states; landing page and dashboard panels render updated state-coverage lists.

---

# Sprint 35: Dashboard Compliance Document Checklist (Weeks 4-6)

### Epic: Centralized Document Tracking

* **Milestone Goals:** Re-engineer the main dashboard viewport to render a persistent list of required compliance documents with status indicators.  
* **User Stories:**  
  - *As a host,* I want to see a clear checklist of required compliance files directly on my main dashboard, so that I can track my onboarding progress at a glance.  
  - *As an operator,* I want visual indicator badges showing if a document is uploaded, pending review, approved, or rejected, so that I have clear feedback.  
* **Technical Dependencies:** Dashboard React components, `PropertyCompliance` query bindings.  
* **Verification Criteria:** Main dashboard renders compliance checklist cards for the selected property; badges accurately reflect the underlying `properties_compliance.status` value.

---

# Sprint 36: Real-Time "AI-on-Demand" Scraper Agent (Weeks 7-9)

### Epic: Scraper Agentic Automation

* **Milestone Goals:** Implement the cache-miss fallback trigger, build the background Municode/portal crawling agent, and create the expert review admin dashboard.  
* **User Stories:**  
  - *As a host,* I want to enter an address in an unmapped city and have the system research the rules in real-time, so that I don't hit a dead end.  
  - *As a subscriber,* I want scraped rules clearly marked as "Verification Pending", so that I am aware of the data's vetting status.  
* **Technical Dependencies:** BeautifulSoup4 scraping pipelines, Gemini 1.5 Pro scraper parsing prompts, WebSocket notifications, admin verification panel.  
* **Verification Criteria:** Entering an unmapped location triggers `tasks.run_agent_compliance_scraper` asynchronously; agent correctly crawls portals and extracts zoning variables via Gemini; "AI-Scraped (Verification Pending)" banner displays on dashboard.

---

# Sprint 37: PDF Form Pre-filling & Package Generator (Weeks 10-12)

### Epic: Document Automation

* **Milestone Goals:** Establish the PDF template database schema, build the coordinate-overlay form pre-filling engine, and package permit folders for zip downloads.  
* **User Stories:**  
  - *As a host,* I want the system to pre-fill official permit and tax application forms with my profile data, so that I avoid typing redundant details.  
  - *As a manager,* I want to download my completed forms and required upload guidelines in a single zip package, so that I can upload them easily to county portals.  
* **Technical Dependencies:** PyPDF2 template form mapping, reportlab overlay layers, Celery zip generation scripts.  
* **Verification Criteria:** Clicking "Generate Permit Package" overlay-fills stored property/host details onto target PDF forms; downloads compiled zip archives containing pre-filled files.

