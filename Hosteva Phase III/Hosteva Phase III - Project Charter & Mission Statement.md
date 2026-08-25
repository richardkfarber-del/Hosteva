# Hosteva — Project Charter & Mission Statement (Phase III: Multi-State GTM & AI Agentic Launch)

# Mission Statement

Hosteva is the definitive, "Compliance-First Property Operations Engine" for the short-term rental (STR) hospitality industry. We bridge the critical market gap between reactive tax compliance tools and operationally intensive property management systems (PMS).

In Phase III, our mission scales from a localized Florida prototype to a nationwide, multi-state commercial platform. By expanding our active coverage to the **top 10 high-volume vacation rental states** (Florida, California, New York, Texas, Colorado, Hawaii, Georgia, North Carolina, Tennessee, and Arizona), Hosteva secures a defensive market footprint. We achieve this scaling through the launch of our **Real-time AI-on-Demand Compliance Agent** and **Pre-filled PDF Permit Application Engine**, turning regulatory complexity into a frictionless, automated onboarding step.

---

# Project Purpose

The primary purpose of Phase III is to execute the commercial launch of Hosteva across 10 high-value states, introducing agentic compliance automation and document-centric dashboards to maximize portfolio conversion.

While Phase II stabilized the core onboarding wizard, Stripe paywall, and basic iCal calendar synchronization, Phase III addresses the final hurdles of national market viability and administrative overhead. This phase enables hosts to:

1. **Access 10 High-Volume States:** Onboard properties across the top vacation rental markets, backed by a pre-compiled database of the most popular tourist destinations.  
2. **Execute AI-on-Demand Compliance Audits:** Instantly analyze codes for unmapped or unincorporated cities in real-time using our background web-scraping research agent, bypassing the limitations of static database lookups.  
3. **Audit Document Checklists on the Dashboard:** View a centralized progress checklist of required compliance files (such as DBPR, HOA, or tax documents) directly on the main dashboard, with status indicators showing upload completion.  
4. **Generate Pre-filled Permit Application Packages:** Automatically pre-fill official municipal permit application forms (PDFs) with stored user and property data, package-assembling the files for one-click download.

---

# Strategic Goals

To ensure a successful and legally defensible launch, Phase III focuses on five core operational and technical pillars:

- **10-State Relational Database Seeding:** Importing the complete, multi-state rules database containing pre-compiled zoning regulations, stay limits, and local discretionary tax percentages for FL, AZ, CA, CO, GA, HI, NC, NY, TN, and TX.  
- **Real-Time "AI-on-Demand" Scraper Agent:** Deploying a Celery-backed, agentic background task that executes targeted web crawls (Municode, local .gov portals) on query cache-misses, parsing unstructured zoning documents into schema-aligned variables using Gemini 1.5 Pro.  
- **Main Dashboard Compliance Checklist:** Restructuring the main viewport to show a persistent, card-based checklist of required files with real-time status tracking.  
- **PDF Form Pre-filling & Assembly Engine:** Integrating a Python-based PDF manipulation pipeline (Pillow, PyPDF, ReportLab) that auto-fills local permit application fields, preparing them for immediate user download.  
- **App-wide Copy & Marketing Alignment:** Overhauling landing page text, wizard titles, and payment gates to reflect Hosteva's new multi-state authority.

---

# Desired Outcomes

| Category / Role | Primary Objective | Key Deliverable / Outcome |
| :---- | :---- | :---- |
| **Individual Hosts (1–5 units)** | Fear-free compliance and visual checklist progress tracking across 10 states. | Centralized dashboard document uploader, real-time "AI-scraped" checklist feedback, and pre-filled PDF downloads. |
| **Professional Property Managers (6–50 units)** | Scalable compliance onboarding for multi-state portfolios. | Direct PDF application form package assembly, reducing overhead and permit processing times to minutes. |
| **Institutional Investors (50+ properties)** | Instant zoning due diligence for national acquisition pipelines. | Real-time AI-on-Demand scraping of complex municipal codes for unmapped markets during property evaluation. |
| **Engineering & Operations** | Zero-downtime database upgrades, scalable scraping, and strict risk guardrails. | High-performance PostgreSQL database, background Celery scraper task queues, and manual expert verification queues. |

---

# Documentation and Governance

The project maintains a centralized, version-controlled repository of all Phase III GTM expansion, architectural, and planning materials to ensure strict compliance and operational continuity.

- **Project Lead:** Richard Keith Farber (Product Owner)  
- **Co-Founder & Advisor:** Brew Lamb  
- **Primary Contractor:** Google Antigravity Engineering Swarm  
- **Effective Date:** June 28, 2026  
- **Reference Materials:**  
  - [Hosteva Go-To-Market Launch Strategy, Feature Matrix, and Roadmap](https://docs.google.com/document/d/1JaykDSyOuuDBKqNgOWkn8wlcDfzd2Phx9iSa03r00Zs/edit)  
  - [Hosteva Jurisdictional Rules DB (Complete)](https://docs.google.com/spreadsheets/d/12hqfOXht9ySzOEwSXBVReE4GTjXT6ea7TikHyUhZHkQ/edit)

