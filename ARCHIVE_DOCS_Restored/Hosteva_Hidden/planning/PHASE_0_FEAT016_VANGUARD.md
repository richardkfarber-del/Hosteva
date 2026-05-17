# Phase 0: Vanguard Planning (Sprint 17: FEAT-016 Recon)
**Date:** 2026-04-16
**Goal:** Research, map, and align the architecture for the Hosteva Dashboard (SPIKE-005) and OTA Compliance Integrations (SPIKE-006) before writing feature code.
**Targets:** SPIKE-005, SPIKE-006

## Vanguard Consensus & Architectural Alignment

**Hawkeye (Product Owner):** 
"For SPIKE-005, Wasp needs to pull the exact Google Stitch design tokens and identify every dynamic variable on the screen (e.g., total active properties, compliance scores, missing permits). For SPIKE-006, Star-Lord is going to hit a wall: Airbnb and Booking.com often require official business verification to access their production POST endpoints. If we can't get production keys, the architecture must support a 'sandbox' or simulated posting flow until we pass their vendor audits."

**Wasp (Lead UI/UX):** 
"If the Google Stitch API rate-limits us or the `.env` keys expire, the dashboard must render a cached state or a skeleton loader. We cannot have a white screen of death. The frontend components must be completely decoupled from the backend data fetching."

**Falcon (Market Recon):** 
"The STR compliance engine (SPIKE-006) can't rely on a single federal API because zoning laws are municipal. We either need to integrate with a massive third-party aggregator (like Rentb.ro or Key Data) or scrape county-level permit registries. The Spike needs to evaluate the cost vs. coverage of an aggregator."

**She-Hulk (CLO - Compliance):** 
"Pushing a user's property address, photos, and calendar to Airbnb (SPIKE-006) requires explicit, GDPR-compliant consent flows built into the Hosteva UI. The backend must log a cryptographically signed timestamp of the user's agreement to the Terms of Service before the API fires the POST request. Furthermore, if the dashboard (SPIKE-005) displays municipal permit violations, the data must be encrypted at rest."

**Star-Lord (Third-Party Integrations):** 
"Airbnb's OAuth2 flow requires a redirect URI. Iron Man needs to ensure our backend router can handle the callback securely, and Vision needs to store the refresh tokens safely in Postgres."

**Iron Man (CTO - Architecture):** 
"The strategy is aligned. Hawkeye's constraints on the board are solid. We'll build the API contracts based on the findings from these two Spikes."