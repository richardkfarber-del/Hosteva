# Hosteva — Production Backlog (Phase III: Multi-State GTM & AI Agentic Launch)

This document details the granular, developer-ready backlog tickets for Phase III. Every ticket conforms to Hosteva's compliance-driven, asynchronous architecture and includes explicit technical execution steps, positive test criteria, and negative test criteria.

---

## Epic 10: Multi-State Expansion & Marketing Overhaul

### HSV-401: Seed the Complete 10-State Jurisdictional Rules Database

- **User Story:** As an STR operator, I want properties in FL, CA, TX, NY, CO, HI, GA, NC, TN, and AZ to automatically pull pre-compiled zoning regulations, so that I can easily assess compliance.  
- **Technical Implementation Details:**  
  - *Database:* Modify `ops/import_rules.py` to read `ops/jurisdictional_rules_complete.csv` (which contains 197+ county and city zoning rules spanning these 10 states).  
  - *Data Normalization:* Ensure the parser handles null values, parses currency values, and converts last verified dates cleanly into python date objects.  
- **AI Verification Criteria:**  
  - **Positive Test:** Executing `python3 ops/import_rules.py` successfully parses the complete 10-state spreadsheet, seeding records into PostgreSQL.  
  - **Negative Test:** Address lookup queries for cities outside of the 10 states handle the missing data gracefully without crashing FastAPI.

### HSV-405: Overhaul App Copy & Branding for 10-State Coverage

- **User Story:** As a prospective subscriber, I want to see clear marketing text across the landing page and subscription gates indicating 10-state coverage, so that I understand the platform's utility.  
- **Technical Implementation Details:**  
  - *Landing Page:* Overhaul landing page text, wizard titles, and checkout panels to explicitly advertise: *"Automating compliance across FL, CA, TX, NY, CO, HI, GA, NC, TN, and AZ."*  
- **AI Verification Criteria:**  
  - **Positive Test:** Navigating to the landing page and billing modals confirms all verbiage and headers are updated dynamically to reflect the 10-state coverage.

---

## Epic 11: Dashboard Checklist & Document Uploader

### HSV-402: Implement Main Dashboard Required Documents Checklist & Indicators

- **User Story:** As a host, I want a unified document checklist on my main dashboard showing required files and their upload status, so that I can easily track my portfolio's compliance.  
- **Technical Implementation Details:**  
  - *Frontend:* Create `src/components/dashboard/DocumentChecklist.tsx` and integrate it onto the main dashboard. Render cards representing required compliance files (such as "DBPR License", "County TDT Certificate", "HOA Approval Letter").  
  - *Status Badges:* Map status badges (`NOT UPLOADED`, `PENDING_REVIEW`, `APPROVED`, `REJECTED`) to the underlying `properties_compliance.status` value.  
- **AI Verification Criteria:**  
  - **Positive Test:** Accessing the main dashboard renders the required checklist cards, with status badges updating in real-time as files transition state.  
  - **Negative Test:** Properties with zero checklist items render a clean "All Compliant" empty state without breaking grid layouts.

---

## Epic 12: Real-time Scraper Agent

### HSV-403: Build Real-time "AI-on-Demand" Scraper Agent Celery Task

- **User Story:** As an STR operator, I want the system to research rules in real-time if my address is in an unmapped city, so that I am never left without compliance support.  
- **Technical Implementation Details:**  
  - *Trigger:* During property registration, check if the city rules are pre-compiled. If a cache-miss occurs, create a temporary `MunicipalCode` record and trigger `tasks.run_agent_compliance_scraper.delay()`.  
  - *Crawler Logic:* In `app/tasks/scraper.py`, implement an asynchronous crawler using BeautifulSoup. Query municipal search engines, filter to `.gov` or `.org` domains, and download zoning texts.  
  - *AI Parsing:* Send raw texts to Gemini 1.5 Pro to parse into structured JSON mapping our DB columns. Update `MunicipalCode` table with `is_ai_scraped = True` and trigger a WebSocket dashboard update.  
- **AI Verification Criteria:**  
  - **Positive Test:** Registering a property in an unmapped city triggers the background Celery scraping task, crawls pages, parses variables, and displays the "AI-Scraped (Verification Pending)" warning badge.  
  - **Negative Test:** Simulated scraper failures or connection blackouts fallback gracefully, displaying a "Rules Under Manual Review" state to the host.

---

## Epic 13: PDF Document Pre-Filling

### HSV-404: Implement PDF Application Form Pre-filling & Download Engine

- **User Story:** As a host, I want the system to pre-fill official permit and tax application forms with my data, so that I avoid typing redundant details.  
- **Technical Implementation Details:**  
  - *Backend:* Create `POST /api/v1/compliance/tasks/{id}/fill-permit` endpoint.  
  - *PDF Overlay:* Use `PyPDF2` to read form templates from the path mapped to `MunicipalCode.form_template_path`. Use `reportlab` to write a transparent overlay containing host name, address, and local tax IDs. Merge the overlay and template.  
  - *Zip Package:* Compress the pre-filled PDF and required guidelines into a `.zip` archive, upload it to storage, and return the download URL.  
- **AI Verification Criteria:**  
  - **Positive Test:** Clicking "Download Permit Package" programmatically pre-fills fields on the PDF template and initiates a zip archive download containing the correct files.  
  - **Negative Test:** If `form_template_path` is missing or null, render an active direct link to the county portal, alerting the user to download the file directly.

