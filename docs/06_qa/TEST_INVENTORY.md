# Hosteva living test inventory

**Ownership**

**Updated:** 2026-09-05 (ET)

- **Hulk** adds a row when shipping a bug fix (regression module or new coverage).
- **Phil Coulson** keeps this inventory current (paths, guards, layers, links).
- **CI** remains the periodic gate (`unit` on every PR + push to `main`).
- **Widow** only for gaps Fury orders (manual / live UAT below).

How to run and CI wiring: see [REGRESSION_AUTOMATION.md](./REGRESSION_AUTOMATION.md).

**Last known green (suite):** **Updated:** 2026-09-05 (ET). Do **not** invent per-module pass/fail here. The gate is **CI on main**. Latest cited tip at inventory write: `75085184f8341d0f04834cc30b28dfb41aef4f56` (merge PR #19) — CI workflow **success** on that push. Re-check Actions on `main` for the current tip.

---

## Automated modules (`tests/` + `app/tests/`)

All rows below are collected by CI job `unit` via:

```bash
python -m pytest tests/ app/tests/ -q --tb=short
```

**Runs when:** every `pull_request` and every `push` to `main` (see `.github/workflows/ci.yml`).

| ID / path | Guards | Layer | Runs when | Last known green | Owner notes |
|-----------|--------|-------|-----------|------------------|-------------|
| `app/tests/test_api.py` | Properties list auth + PII masking + timeout degradation; eligibility check (anon + authenticated) | api | PR / main CI | CI on main is the gate | Core API smoke |
| `app/tests/test_dom.py` | Wizard + dashboard sidebar DOM ids/classes; PL-01 disclaimer layout; sidebar auth uses access token | dom-assert | PR / main CI | CI on main is the gate | PL-01 markers |
| `tests/test_ai_compliance_auditor.py` | Document audit success / name+address mismatch / expired date; checklist-items fetch | api | PR / main CI | CI on main is the gate | Auditor upload path |
| `tests/test_audit_v1.py` | Celery OCR task success + pending-review on mismatch | unit | PR / main CI | CI on main is the gate | Task-level (mocked OCR) |
| `tests/test_billing_v1.py` | Checkout unauthorized / kill-switch 503 / subscription+permit success; Stripe webhook subscription+permit complete | api | PR / main CI | CI on main is the gate | Enables `BILLING_ENABLED` locally; not live Stripe |
| `tests/test_bug_pl02_street_view.py` | Street View / Places fetch: geocode retry before stock; fallback helpers; dashboard “Street View unavailable” label | unit | PR / main CI | CI on main is the gate | BUG-PL-02; image *quality* still Widow |
| `tests/test_bug_pl05_evaluate.py` | `POST .../evaluate` must not claim Compliant for Restricted / checklist / non-compliant zoning | api | PR / main CI | CI on main is the gate | BUG-PL-05 |
| `tests/test_bug_pl07_create_500.py` | Property create must return 201 (not 500) when geocode / image / audit / municipal seed fail; corridor + MB cases | api | PR / main CI | CI on main is the gate | BUG-PL-07 |
| `tests/test_bug_us006_checklist_500.py` | Free checklist-items / tasks return **403 not 500**; relationship boom still 403; simulate flag path | api | PR / main CI | CI on main is the gate | BUG_US006 |
| `tests/test_bug_us006_simulate_500.py` | `simulate-entitlement` returns 200 when `ALLOW_BILLING_SIMULATION=true`; `/me` + checklist after simulate | api | PR / main CI | CI on main is the gate | BUG_US006_SIMULATE_500 |
| `tests/test_calendar_v1.py` | iCal sync registration + Celery sync task; calendar export success / invalid token | api | PR / main CI | CI on main is the gate | Calendar v1 |
| `tests/test_compliance_address.py` | Compliance-by-address; Orange County Thin→UR; HOA match; miss UR; missing+empty address params | api | PR / main CI | CI on main is the gate | Address lookup + Curated gate |
| `tests/test_compliance_endpoint.py` | Compliance get/search (+ fallbacks); task chat; agent trigger; fill-permit-form | api | PR / main CI | CI on main is the gate | Broader compliance API |
| `tests/test_eligibility_mb_city_of.py` | “City of Miami Beach” municipal alias; MB Convention Center eligibility allowed+checklist (not stuck UNDER_REVIEW) | api | PR / main CI | CI on main is the gate | Cheap MB seed guard |
| `tests/test_eligibility_no_hash.py` | TE-002: no hash-lottery GREEN/YELLOW/RED; removed `determine_status`; under-review without muni | unit | PR / main CI | CI on main is the gate | TE-002 |
| `tests/test_epic_auth.py` | US-012 register password policy; US-013 change-password; US-014 forgot/reset token-hash + anti-enumeration; auth page hrefs | api | PR / main CI | CI on main is the gate | EPIC-AUTH; Resend *delivery* is Widow |
| `tests/test_hoa_upload.py` | HOA document upload success path | api | PR / main CI | CI on main is the gate | HOA upload |
| `tests/test_inbox_v1.py` | Inbox unauthorized; incoming guest message + suggested reply; authorized list; reply success | api | PR / main CI | CI on main is the gate | Inbox v1 |
| `tests/test_password_policy.py` | US-012 shared password policy accept/reject rules | unit | PR / main CI | CI on main is the gate | Shared helper |
| `tests/test_phase1_launch.py` | ToS / Privacy / Features / About 200; waitlist submit; landing tiers+disclaimer; under-review flag; sidebar profile widget | api | PR / main CI | CI on main is the gate | Launch + legal pages; overlaps US-010 positioning |
| `tests/test_phase_b_us002_us003_us004.py` | UNDER_REVIEW never `is_compliant`; MB covered; Bay/Broward checklist gov source URLs; wizard→register→dashboard address handoff markers | api | PR / main CI | CI on main is the gate | Phase B US-002/003/004 |
| `tests/test_properties_v1.py` | `POST /api/properties/` unauthorized / success (image mocked) / validation error | api | PR / main CI | CI on main is the gate | Properties v1 create |
| `tests/test_seed_rules.py` | `seed_rules` parsers (days/occupancy/tax/date) + upsert behavior | unit | PR / main CI | CI on main is the gate | Spreadsheet seed script |
| `tests/test_te001_auth_checkout.py` | TE-001: unauth checkout 401 (no session create); auth checkout uses real host id; kill-switch 503 before Stripe | api | PR / main CI | CI on main is the gate | TE-001; never `user_mock_123` |
| `tests/test_us006_entitlement.py` | Free vs Essentials checklist/task gating; webhook sim activates Essentials on `/me`; simulate blocked in production | api | PR / main CI | CI on main is the gate | US-006 |
| `tests/test_us010_positioning_pages.py` | `/features` + `/about` real pages; Florida-depth copy; no live “operations engine” claim; meta scrubbed of competitor names | dom-assert | PR / main CI | CI on main is the gate | US-010 / BUG-PL-04 companion |
| `tests/test_user_me_guest_fix.py` | `/api/user/me` must not collapse Bearer hosts into Guest; shape parity; missing host ≠ Guest label | api | PR / main CI | CI on main is the gate | Guest identity bug |
| `tests/test_validation_engine.py` | Agnostic validate: reject zoning / property type / stay duration; allowed → checklist generation | api | PR / main CI | CI on main is the gate | Validation engine |
| `tests/test_validation_workflow.py` | Hillsborough nightly reject / weekly allowed+checklist; St. Petersburg warning+checklist; Pasco permit+checklist | api | PR / main CI | CI on main is the gate | County workflow fixtures |

**Module count:** 29 (`2` under `app/tests/`, `27` under `tests/`).

---

## Live smoke (`scripts/smoke_live.sh`)

| Item | Guards | Layer | Runs when | Last known green | Owner notes |
|------|--------|-------|-----------|------------------|-------------|
| `scripts/smoke_live.sh` (+ CI job `smoke_live`) | Auth-less GETs: `/`, `/login`, `/features`, `/about`; optional `/health` (404 = skip) against `LIVE_BASE_URL` (default `https://gethosteva.com`) | live smoke | **`workflow_dispatch` only** — not every PR | Manual / dispatch result; not the PR gate | See [REGRESSION_AUTOMATION.md](./REGRESSION_AUTOMATION.md) |

---

## Widow-only / manual (not CI)

Keep on Widow / human UAT. Fury orders gaps here; do not pretend CI covers them.

| Gap | Why not CI |
|-----|------------|
| Stripe Checkout redirect + webhook entitlement (real Stripe / live kill-switch) | Needs live billing + real Checkout / webhooks |
| Resend mail E2E (forgot / reset delivery to a real inbox) | Needs live email + DNS; suite only checks anti-enumeration / token-hash paths |
| Street View / Places **image quality** and real-address overlay (“Street View unavailable”) | Visual / Places quota / real geocode; unit covers retry+fallback logic only |
| Full browser UAT (dashboard DOM, multi-property UX walks, signed-in prod session) | Browser session against production / staging |
| SEO / marketing copy reviews beyond unit string asserts | Editorial judgment |
| Any probe that needs a signed-in browser session against production | Out of `unit` + auth-less smoke scope |

---

## Maintenance checklist

1. New automated module under `tests/` or `app/tests/` → add a row in the table above in the same PR when practical.
2. Bug-fix PR from Hulk → add or cite the regression module row.
3. Phil Coulson refreshes “Last known green” tip citation when documenting a main merge (still: **CI on main is the gate**; no invented pass/fail).
4. Quarantine (`xfail`) must stay rare — see REGRESSION_AUTOMATION.md quarantine policy.
