# Product UX Regression Audit
**Auditor**: Hawkeye (Product Manager)
**Focus**: Product and Feature flow on live site, specifically the Free Address Check pipeline.

## Executive Summary
A critical UX regression exists within the "Free Address Check" pipeline (`/wizard`). While the backend routing for eligibility checks was successfully built out to use a robust Google Maps integration (`/api/eligibility/check`), the frontend UI in `wizard.html` was not wired up to use it. Instead, the UI continues to hit a hardcoded, mock backend stub (`/wizard/audit`) that ignores actual geospatial processing and simply returns a dummy "Pass/Fail" based on whether the string "fl" is present. 

## Detailed Findings

### 1. Free Address Check Pipeline (`/wizard`) - **Critical Regression**
- **Autocomplete Functionality**: The autocomplete feature works correctly. It successfully hits the live `GOOGLE_MAPS_API_KEY` mapped to `/api/eligibility/autocomplete` and displays valid real-time address suggestions.
- **Audit Execution Mismatch**: When the user clicks "Run Compliance Audit", the client-side JavaScript calls the mock endpoint `/wizard/audit` defined in `main.py` instead of the production API (`/api/eligibility/check` in `eligibility.py`).
- **Data Integrity / UX Break**: The dummy `/wizard/audit` endpoint overrides the real status checks (Traffic Light System: GREEN, YELLOW, RED) by hardcoding "Pass" for addresses containing "fl" or "florida", and "Fail" for everything else. This completely bypasses the real logic and returns inconsistent dummy text to the UI.

### 2. Product Consistency (`/dashboard` vs `/wizard`) - **Gap**
- While `/wizard` relies on the mock `/wizard/audit` endpoint, the newly built Host Dashboard (`/dashboard`) actually correctly triggers `/api/eligibility/check` under the hood. This represents a major product consistency break—an address queried from the main Dashboard will correctly parse through the Geocoding API and assess restrictions, while the identical property run through the standalone Wizard gets dummy data.

## Recommendations for Remediation
1. **Refactor `wizard.html` fetch logic**: Update the client-side fetch call in `templates/wizard.html` from `fetch('/wizard/audit', ...)` to `fetch('/api/eligibility/check', ...)`.
2. **Harmonize Response Models**: The `wizard.html` UI relies on data keys (`data.message`, `data.status`, `data.details`) that differ from the actual `/api/eligibility/check` payload (which returns `jurisdiction`, `status: GREEN/YELLOW/RED`, `conditions`, and `components`). The frontend template needs to be updated to map to the correct payload shape.
3. **Deprecate Dummy Route**: Remove the `@app.post("/wizard/audit")` endpoint from `main.py` to prevent any further routing regressions.
