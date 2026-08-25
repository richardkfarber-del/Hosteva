# Hosteva — Core Feature Set (GTM Launch Strategy Phase)

# 1\. Introduction & GTM MVP Scoping

This document details the core Minimum Viable Product (MVP) features required for Hosteva's commercial go-to-market launch in the Florida short-term rental (STR) sector. In alignment with our GTM strategy, the feature set is prioritized to stabilize the core onboarding loop, integrate automated document auditing, and deliver simple, robust calendar synchronization while minimizing regulatory and API dependency overhead.

---

# 2\. Core MVP Features

## Feature 1: Dynamic Compliance Checklist Engine

* **Description:** A logic-driven compliance engine that maps state, county, and city-level rules directly to specific property profiles.  
* **Functional Capabilities:**  
  - **Rules-to-Property Mapping:** Automatically processes geocoded property addresses to extract the correct jurisdiction (e.g., matching the property to Broward County or the City of Destin).  
  - **Dynamic Task Generation:** Automatically compiles a hyper-localized checklist of required licenses, safety certifications, and tax registrations based on the rules database.  
  - **Idempotent Recalculations:** Updates checklist tasks dynamically if property attributes (such as occupancy limits or property types) are modified by the host.

## Feature 2: Guided Onboarding Wizard

* **Description:** An intuitive, multi-step property registration wizard that performs zoning pre-validation before database persistence.  
* **Functional Capabilities:**  
  - **Zoning Pre-Validation:** Integrates address geocoding to instantly cross-reference county-level zoning boundaries. If the property is in a restricted STR zone, it flags a warning to the user before adding the property.  
  - **Address Query Parsing:** Resolves raw autocomplete addresses, preserving the query parameter seamlessly as the user navigates from the landing page to `/wizard`.  
  - **Visual Verification:** Pulls Google Street View imagery of the geocoded address to render a high-quality visual card of the property, establishing an institutional feel.

## Feature 3: AI Document Auditor (OCR & Validation)

* **Description:** An automated document checker that leverages Gemini 1.5 Pro to validate proof-of-compliance files (such as DBPR licenses, HOA bylaws, lease agreements, or local tax docs) uploaded by hosts.  
* **Functional Capabilities:**  
  - **Multi-Document OCR Scan:** Accepts uploaded files (PDF, PNG, JPG) representing HOA declarations, sales tax certificates, or safety permits.  
  - **AI Metadata Extraction:** Gemini extracts key fields (such as license numbers, expiration dates, owner names, and address strings) and verifies that they align with the property's profile.  
  - **State Queue Management:** Enqueues documents in a system-wide status queue (`PENDING`, `APPROVED`, `REJECTED`) and renders clear error codes if validation fails (e.g., "Address Mismatch").

## Feature 4: Regulatory Portal Integration & Permit Package Generator

* **Description:** Aggregates manual registration links and auto-fills permit documents to minimize administrative friction.  
* **Functional Capabilities:**  
  - **Direct Portal Redirections:** Since government API systems are heavily gated, Hosteva acts as the aggregator, providing direct, hyper-localized links to county and state application portals (e.g. the Broward County short-term rental application page).  
  - **Permit Document Pre-filling:** Auto-fills local county permit application forms with stored host and property data, package-assembling the files for easy manual upload.

## Feature 5: Operational Core & Stripe Payment Gateway

* **Description:** Integrates billing gateways for subscription management and provides simple, highly reliable calendar sync to prevent booking conflicts.  
* **Functional Capabilities:**  
  - **Stripe Subscription Gateway:** Automatically manages the paywall tiers (Free, Starter, Growth, Enterprise) and handles the $150 transactional add-on for direct permit processing.  
  - **Simple Multi-Calendar Sync (iCal Fallback):** Due to strict API partnership gates on major OTAs (Airbnb, Vrbo), direct 1-click syndication is strategically delayed for early MVP. Instead, Hosteva implements a highly reliable, standard iCal import/export loop to synchronize calendars, block double-bookings, and track gross payouts asynchronously without direct API overhead.

