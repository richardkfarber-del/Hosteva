# PL-13 GO — Checklist CTA + Tax Registration URL

**Status:** Locked (Cap DoR not on GitHub at intake; this file is source of truth.)  
**Tickets:** US-020, US-021, TE-013

## Product goals

1. **Remove “Open free checklist”.** Drop that string/CTA from wizard, dashboard, and tests. Covered guests keep **Sign Up** (US-015). Logged-in Covered use **Eligibility Audit** (wizard checklist on-page) and dashboard **Before you list** only — no redundant free-checklist button.

2. **Split Municipal Code vs Tax Registration URLs.** Checklist builder must not copy `municipal_code.source_url` onto tax tasks. Wizard Tax Registration must use a dedicated `tax_registration_url`.

3. **Pasco control (10703 Oak Drive, Hudson, FL 34667).** Tax Registration primary link = `https://pasco.county-taxes.com/tourist` (Tourist Express). **Not** `https://floridarevenue.com/Forms_library/current/dr15tdt.pdf`. Info-only secondary may cite `https://www.pascotaxes.com/taxes/tdt/` (not the primary CTA).

## Out of scope

- Do not expand Curated allowlist
- Do not change Under Review gate for incomplete addresses
- No legal-advice copy

## Done when

- No “Open free checklist” in UI templates
- Pasco tax checklist/link uses Tourist Express
- Municipal `source_url` is not forced onto tax items
- Tests updated; CI green
