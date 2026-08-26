# Hosteva — Core Feature Set (Phase III: Multi-State GTM & AI Agentic Launch)

# 1\. Introduction & Phase III MVP Scoping

This document details the core Minimum Viable Product (MVP) features required for Hosteva's Phase III commercial launch. In alignment with our GTM expansion, the feature set is prioritized to scale active coverage to **the top 10 vacation rental states in the United States**, deploy a real-time agentic web scraper for unmapped markets, implement central dashboard document tracking, and deliver an automated PDF permit form generator.

These features complete the end-to-end "compliance-as-a-service" loop, providing hosts with a frictionless path from onboarding to fully pre-filled license submissions.

---

# 2\. Core MVP Features

## Feature 1: Dynamic 10-State Coverage Database

* **Description:** Expands Hosteva's active compliance checker database from unincorporated Florida to the top 10 vacation rental states, capturing all tourist destinations and large population zones.  
* **Functional Capabilities:**  
  - **10-State Seed Data:** Onboards pre-compiled rules, tax percentages, and local permit regulations for Florida, California, New York, Texas, Colorado, Hawaii, Georgia, North Carolina, Tennessee, and Arizona.  
  - **Address Geocoding Integration:** Integrates structured address parsing (City, State, Zip, County) to instantly identify and match target properties to their regional jurisdictions within these 10 states.

## Feature 2: Main Dashboard Compliance Checklist & Document Uploader

* **Description:** Re-engineers the principal user dashboard viewport to place required compliance documents front-and-center, with persistent upload statuses.  
* **Functional Capabilities:**  
  - **Main Dashboard Checklist:** Renders a list of mandatory compliance documents (e.g. "DBPR License", "County TDT Certificate", "HOA Approval Letter") directly on the central property dashboard.  
  - **Real-Time Status Indicators:** Visual tags (`NOT UPLOADED`, `PENDING_REVIEW`, `APPROVED`, `REJECTED`) indicating document health.  
  - **Frictionless Upload Access:** Clicking a checklist item opens a context-specific modal or transitions the user directly to the task uploader page.

## Feature 3: Real-Time "AI-on-Demand" Scraper Agent

* **Description:** A robust, agentic background task runner that executes on-demand compliance research when a user inputs an address outside our pre-compiled database.  
* **Functional Capabilities:**  
  - **Database Match Check:** On property registration, the backend checks if the city or county rules are pre-compiled. If a record is found, the rules load instantly.  
  - **Agentic Scraping Pipeline:** If no match is found, the system displays a loading indicator (*"Analyzing local municipal codes in real-time..."*) and triggers a background Celery agent.  
  - **Web Crawler & Citation Parser:** The agent crawls search engines targeting local government portals (`.gov`, `.org`), Municode, or American Legal Publishing. It extracts the zoning rules, normalizes variables to match our database schemas, and extracts the direct source URL citation.  
  - **Verification Gating:** Instantly displays extracted rules to the host with an **"AI-Scraped (Verification Pending)"** warning badge on their dashboard. It automatically queues the record in our admin control panel for expert review before permanently committing it to the master database.

## Feature 4: PDF Permit Form Pre-filling & Download Engine

* **Description:** Pre-fills official local permit and tax registration forms programmatically using stored host and property data.  
* **Functional Capabilities:**  
  - **PDF Template Repository:** An organized, secure backend folder containing official PDF application form templates (e.g. Florida DBPR Form HR-7020, county BTR forms, and local discretionary tax forms).  
  - **Automated Field Injection:** A Python-based PDF manipulation worker (using `PyPDF2` and `reportlab` or form-fill utilities) that overlays geocoded user data, address strings, and contact details onto the PDF form fields.  
  - **1-Click Package Download:** Packages the pre-filled PDF alongside a checklist of required upload files as a single, downloadable `.zip` package. This supports the **$150 direct permit processing add-on** monetized inside our subscription engine.

## Feature 5: Multi-State Marketing Copy & UI Overhaul

* **Description:** Overhauls platform copy, advertisements, and page headings to announce nationwide, multi-state capability.  
* **Functional Capabilities:**  
  - **Landing Page Advertising Copy:** Updates headers and sub-features to declare: *"Compliance Automation across FL, CA, TX, NY, CO, HI, GA, NC, TN, and AZ — covering the vast majority of active US vacation rentals."*  
  - **Subscription Paywall Alignment:** Updates payment screens to emphasize multi-state protection and ongoing regulatory change alerting.

