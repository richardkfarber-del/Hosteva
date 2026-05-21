# Municipal Code to Technical Compliance Audit
**Date:** 2026-04-15
**Auditor:** Jennifer Walters (She-Hulk)
**Target:** Address Eligibility Module (Florida)

## Executive Summary
This document provides the legal-to-technical compliance mapping for the Hosteva Address Eligibility module. It ensures that the technical constraints enforced by the system perfectly mirror the municipal codes for the supported jurisdictions.

## Jurisdiction: Pasco County

### 1. Short-Term Rental Permit
*   **Municipal Code:** Pasco County Code Chapter 134
*   **Legal Requirement:** A Short-Term Rental Business Tax Receipt is required.
*   **Technical Mapping:** `florida_compliance_engine.py` validates `has_permit == True`. If false, execution is halted with an error.
*   **Status:** **[COMPLIANT]**

### 2. Occupancy Limits
*   **Municipal Code:** Pasco County Code 134-3
*   **Legal Requirement:** Maximum occupancy limit per dwelling unit.
*   **Technical Mapping:** The system strictly enforces `num_guests <= 10`.
*   **Status:** **[COMPLIANT]**

### 3. Parking Requirements
*   **Municipal Code:** Pasco County Code 134-4
*   **Legal Requirement:** Off-street parking required based on bedroom count.
*   **Technical Mapping:** The system calculates `parking_spaces >= (num_bedrooms * 1)`.
*   **Status:** **[COMPLIANT]**

### 4. Fire Safety
*   **Municipal Code:** Florida Fire Prevention Code
*   **Legal Requirement:** Fire extinguisher and smoke alarms required.
*   **Technical Mapping:** The system validates `has_fire_safety == True`.
*   **Status:** **[COMPLIANT]**

### 5. Noise Ordinance
*   **Municipal Code:** Pasco County Code 14-31
*   **Legal Requirement:** Quiet hours 22:00-07:00.
*   **Technical Mapping:** Currently documented in `PASCO_CODES` dictionary but **lacks a discrete technical execution check** during the evaluation phase.
*   **Status:** **[NON-COMPLIANT / GAP]** - Requires Dev Team intervention to add noise monitoring equipment verification or host-agreement validation.

---

## Jurisdiction: Hillsborough County

### 1. Vacation Rental License
*   **Municipal Code:** Hillsborough County Code Chapter 30
*   **Legal Requirement:** Hillsborough County Vacation Rental License required.
*   **Technical Mapping:** The system validates `has_vacation_license == True`.
*   **Status:** **[COMPLIANT]**

### 2. State Registration
*   **Municipal Code:** Florida Statute 509.242
*   **Legal Requirement:** DBPR registration required.
*   **Technical Mapping:** The system validates `has_state_registration == True`.
*   **Status:** **[COMPLIANT]**

### 3. Occupancy Limits
*   **Municipal Code:** Hillsborough County Code 30-5
*   **Legal Requirement:** Maximum occupancy limit per dwelling unit.
*   **Technical Mapping:** The system strictly enforces `num_guests <= 12`.
*   **Status:** **[COMPLIANT]**

### 4. Parking Requirements
*   **Municipal Code:** Hillsborough County Code 30-6
*   **Legal Requirement:** Stricter parking ratios.
*   **Technical Mapping:** The system calculates `parking_spaces >= (num_bedrooms * 2)`.
*   **Status:** **[COMPLIANT]**

### 5. Annual Inspection Requirement
*   **Municipal Code:** Hillsborough County Code 30-8
*   **Legal Requirement:** Annual safety inspection required.
*   **Technical Mapping:** The system dynamically calculates `days_since_inspection <= 365` against the current UTC timestamp.
*   **Status:** **[COMPLIANT]**

## Legal Mandate
The dev team (Iron Man/Rocket) must patch the Pasco Noise Ordinance gap. Until the technical pipeline can actively verify compliance with Code 14-31, Pasco evaluations are legally incomplete. The BDD spec (`tests/features/compliance_audit_florida.feature`) has been updated to reflect these strict boundaries.