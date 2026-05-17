# Generic Zoning & Compliance Engine Audit
**Date:** 2026-04-15
**Auditor:** Jennifer Walters (She-Hulk)
**Target:** Dynamic Compliance Engine (app/services/compliance_engine.py)

## Executive Summary
In addition to the hardcoded Florida county rules, the system contains a dynamic, database-driven `ComplianceEngine`. This audit maps the technical constraints of this generic engine to standard municipal legal principles.

## Legal to Technical Mapping: Dynamic Engine

### 1. Land Use Permissibility (Zoning Category)
*   **Legal Principle:** A specific land use (e.g., Short-Term Rental) must be explicitly permitted within a defined zoning district (e.g., R-1 Single Family).
*   **Technical Mapping:** The engine queries `ZoningRegulation` by `zoning_district_id` and `land_use_type_id`. It enforces `reg.is_permitted == True`. If false, it throws a "Not permitted" violation.
*   **Status:** **[COMPLIANT]** - Safely blocks unauthorized land uses.

### 2. Minimum Threshold Requirements
*   **Legal Principle:** Certain rules require a minimum threshold (e.g., minimum lot size, minimum stay duration of 7 days).
*   **Technical Mapping:** The engine compares the submitted property value against `reg.min_value`. If `actual_val < float(reg.min_value)`, it flags a "Below minimum" violation.
*   **Status:** **[COMPLIANT]**

### 3. Maximum Capped Limits
*   **Legal Principle:** Certain rules cap activities (e.g., maximum occupancy, maximum consecutive rental days).
*   **Technical Mapping:** The engine compares the submitted property value against `reg.max_value`. If `actual_val > float(reg.max_value)`, it flags an "Above maximum" violation.
*   **Status:** **[COMPLIANT]**

### 4. Mandatory Documentation / Verifications
*   **Legal Principle:** Certain documents or safety checks are strictly required, regardless of numeric value.
*   **Technical Mapping:** If no value is provided, but `reg.is_required == True`, the engine flags a "Missing required value" violation.
*   **Status:** **[COMPLIANT]**

## Conclusion
The `ComplianceEngine` dynamically translates municipal zoning codes into four technical constraints: Boolean Permissibility, Min/Max Numeric boundaries, and Mandatory field presence. The architecture is legally sound and prevents invalid state execution.
