# PL-13 backlog — Checklist CTA + Tax Registration URL

Locked decisions from `docs/00_intake/PL13_CHECKLIST_CTA_AND_TAX_URL_GO.md`.

## US-020 — Remove “Open free checklist”

**Intent:** Covered guests still Sign Up (US-015). Logged-in Covered do not get a second free-checklist button.

| Surface | After |
|---------|--------|
| Wizard guest Covered | Sign Up + helper + honesty (unchanged) |
| Wizard logged-in Covered | Checklist ready + honesty; items on Eligibility Audit; no free-checklist button |
| Dashboard Covered | **Before you list** only |
| Under Review | Unchanged honesty / no checklist promise |

## US-021 — Oak Drive Tax Registration

Control address: **10703 Oak Drive, Hudson, FL 34667** (Pasco Curated).

| Link | URL |
|------|-----|
| Tax Registration **primary** | `https://pasco.county-taxes.com/tourist` |
| Must **not** be primary | `https://floridarevenue.com/Forms_library/current/dr15tdt.pdf` |
| Info-only secondary (optional cite) | `https://www.pascotaxes.com/taxes/tdt/` |
| Municipal ordinance `source_url` | County municipal site (not the tax portal) |

Municipal ≠ tax. Permit/ordinance citations stay on `source_url`.

## TE-013 — `tax_registration_url` wiring

- Add `municipal_codes.tax_registration_url` (model + schema + migration + `init_db` column add).
- Checklist builder: permit → `source_url`; tax → `tax_registration_url` (never copy municipal onto tax).
- Wizard: ordinance link uses `source_url`; Tax Registration link uses `tax_registration_url`.
- Pasco pack seed (`scripts/seed_tampa_bay_rules.py`) sets both fields.
- Tests: Oak Drive tax item = Tourist Express; municipal URL ≠ tax URL; no “Open free checklist” in templates.
