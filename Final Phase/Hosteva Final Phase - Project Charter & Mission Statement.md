# Hosteva — Project Charter & Mission Statement (GTM Launch Strategy Phase)

# Mission Statement

Hosteva's mission is to serve as the definitive "Compliance-First Property Operations Engine" for the short-term rental (STR) hospitality industry. We bridge the critical market gap between reactive tax compliance automation and operationally intensive property management systems (PMS). By integrating regulatory adherence directly into the operational onboarding workflow, Hosteva guarantees that property listings are established on a foundation of absolute legal validity, protecting hosts from severe daily municipal penalties and deactivation.

---

# Business Problem & Strategic Market Opportunity

The STR software market is heavily divided between specialized tax compliance tools and generalist property management systems, leaving a major structural gap for compliance management:

| Competitor | Focus Area | Key Limitations | Hosteva Differentiation |
| :---- | :---- | :---- | :---- |
| **Avalara MyLodgeTax** | Occupancy tax automation | High fee structure; no zoning lookups, HOA validation, or guest communication tools. | Comprehensive regulatory audits including zoning, HOA validation, and pre-validation wizard. |
| **Guesty** | Enterprise-scale PMS | Complex interface; high pricing ($20-$50/unit/month plus setup fees); compliance is secondary. | Lightweight operator experience with compliance-driven onboarding from listing inception. |
| **Hostaway** | Growth-oriented PMS | Generalist management features; compliance is treated as a manual, external process. | Regulatory and municipal compliance prioritized at listing creation to prevent violation exposure. |
| **Hospitable.com** | Messaging automation | Narrow focus on messaging; lacks robust compliance checks or document auditing. | Unified AI inbox paired with comprehensive compliance tracking and verification checks. |

---

# The Paywall & Monetization Strategy

Hosteva utilizes a "compliance hook" to drive initial user acquisition, transitioning hosts into recurring revenue tiers based on portfolio size and feature depth:

## Tiered SaaS Pricing Model

* **Free Tier (The Compliance Hook):** Includes address lookups, geocoding validation, and basic municipal checklist generation to demonstrate immediate value.  
* **Starter Tier ($29/month/property):** Enables active compliance tracking, basic multi-calendar synchronization, and the AI Document Auditor (capped at 5 documents/month).  
* **Growth Tier ($59/month/property):** Offers unlimited AI Document Audits, multi-channel syndication support, ongoing regulatory change scanning, and the Unified AI Inbox with AI-generated messaging suggestions.  
* **Enterprise / Portfolio Tier ($149/month/property):** Features custom compliance configurations, dedicated local LLM deployments, and automated local tax filing.

## Transactional Add-on

* **Direct Permit Processing ($150 per submission \+ municipal fees):** Provides a high-margin transactional revenue stream for hosts requiring manual or guided registration assistance.

---

# Desired Outcomes

| Category / Role | Primary Objective | Key Deliverable / Outcome |
| :---- | :---- | :---- |
| **Individual Hosts (1–5 units)** | Fear-free compliance and basic multi-channel syncing. | Basic compliance checklist, geocoded verification, and automated iCal calendar blocking. |
| **Professional Property Managers (6–50 units)** | Centralized portfolio tracking and AI document validation. | 100% automated document audits via OCR, reducing manual registration review time to seconds. |
| **Institutional Investors (50+ units)** | Pre-acquisition zoning checks and automated tax filing. | Instant zoning pre-validation before property acquisition, minimizing legal and financial risk. |
| **Engineering & Operations** | Clean tech stack boundaries and idempotent setups. | Automated SQLite database migrations, structured seeding pipeline, and high-concurrency FastAPIs. |

