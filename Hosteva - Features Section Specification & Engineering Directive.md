# Phase I Master Engineering Directive & Defect Remediation Specification (v2.0)

## 1\. Executive Summary & Sprint Scope

This directive establishes the finalized Phase I launch scope for Hosteva. The primary focus is the "Compliance Essentials" tier ($9.99/mo or $99/yr), delivering immediate value through compliance research. Complex operational automation features are formally deferred to Phase II.

## 2\. Navigation & Header Directives

1. Completely hide/remove the "Security" link from desktop and mobile navigation.  
2. Re-route "Features" navbar link to anchor to \#features on the landing page or /features.

## 3\. Features Section UI & Content Specification

### Tier 0 — Free ($0)

Includes basic address lookup and preliminary zoning risk assessment.

### Tier 1 — Compliance Essentials ($9.99/mo or $99/yr)

Includes full interactive compliance checklists, direct government portal links, municipal fee schedules, AI chat assistant, and ordinance/renewal alerts.

### Coming Soon (Phase II Pipeline)

Pre-filled PDF permit application generator, AI listing optimizer, and AI OCR document auditor. Note: OTA 1-click publishing and multi-calendar sync are deferred from marketing.  
Refer to the Stitch visual design in: projects/Hosteva/features\_design.

## 4\. Defect Remediation & Platform Enhancements

Task 1: Post-Registration Property Context Persistence. Ensure searched addresses from /wizard pass through /register so new user accounts land on the /dashboard with their property data pre-populated.  
Task 2: Footer Legal Disclaimers & Policy Links. Wire Privacy/Terms links. Include disclaimer: 'Hosteva is an automated compliance research tool and does not provide legal advice; hosts are responsible for final filings.'  
Task 3: Unincorporated & Cache-Miss Graceful Fallback. Implement a visual 'Jurisdiction Under Review / AI Scraping in Progress' badge for addresses without pre-compiled rules.  
Task 4: Outbound Government Link Security & UX. All external .gov links must use target='\_blank' rel='noopener noreferrer' and include external link indicators.  
Task 5: Dashboard Sidebar Feature Flagging. Quarantine AI Media Studio, Calendar/Operations, and Unified Inbox behind ENABLE\_OPERATIONS\_MODULE=False.

## 5\. Technical Implementation & QA Acceptance Criteria

1. Security link is inaccessible in all viewport sizes.  
2. Features link correctly navigates to the \#features anchor.  
3. Registration successfully persists address data to the user dashboard.  
4. Footer disclaimer is visible and all policy links are active.  
5. Fallback state triggers correctly for unsupported jurisdictions.  
6. Feature flags successfully hide restricted modules in production environments.

