# Regression automation

Lean GitHub Actions gate for Hosteva. Does **not** replace Widow (browser) UAT.

**Living checklist:** full module inventory (every `test_*.py`), ownership rules, Widow-only gaps, and live-smoke rows live in [TEST_INVENTORY.md](./TEST_INVENTORY.md). This file is how-to-run / CI overview only.

## What CI runs

### `unit` (every `pull_request` + `push` to `main`)

- Ubuntu + Python 3.12
- `pip install -r requirements.txt` plus `pytest` / `httpx` (not pinned in requirements)
- Env (test-only; does not change Render / prod billing):
  - `DATABASE_URL` / `INTERNAL_DATABASE_URL` = sqlite
  - `ENVIRONMENT=testing`
  - `JWT_SECRET_KEY`, `VIBRANIUM_ENCRYPTION_KEY` (CI placeholders)
  - `BILLING_ENABLED=false` (prod-like kill-switch; tests that need checkout enable it locally)
- Command:

```bash
python -m pytest tests/ app/tests/ -q --tb=short
```

`app/tests/conftest.py` and `tests/conftest.py` set the same sqlite / JWT baseline. Individual modules may override DB URLs for isolation.

Module-by-module inventory: [TEST_INVENTORY.md](./TEST_INVENTORY.md).

### `smoke_live` (`workflow_dispatch` only)

- Does **not** run on every PR
- `bash scripts/smoke_live.sh` against `LIVE_BASE_URL` (default `https://gethosteva.com`)
- Auth-less GETs: `/`, `/login`, `/features`, `/about`, and `/health` if present (404 = skip)

## Local command

From the repo root (with deps + pytest installed):

```bash
export DATABASE_URL=sqlite:///./test_ci.db
export INTERNAL_DATABASE_URL=sqlite:///./test_ci.db
export ENVIRONMENT=testing
export JWT_SECRET_KEY=TEST_SECRET_KEY
export BILLING_ENABLED=false
# optional: VIBRANIUM_ENCRYPTION_KEY (Fernet); tests/conftest generates one if unset
python -m pytest tests/ app/tests/ -q --tb=short
```

Live smoke:

```bash
LIVE_BASE_URL=https://gethosteva.com bash scripts/smoke_live.sh
```

## Widow-only (manual — not in this gate)

Canonical gap list: [TEST_INVENTORY.md § Widow-only](./TEST_INVENTORY.md#widow-only--manual-not-ci). Keep these on Widow / human UAT; CI does not cover them:

- Stripe Checkout redirect + webhook entitlement (real Stripe / live kill-switch)
- Street View / Places image quality and “Street View unavailable” overlay on real addresses
- Auth email delivery (Resend) forgot/reset flows end-to-end
- Full dashboard DOM / multi-property UX walks
- SEO / marketing copy reviews beyond unit string asserts
- Any probe that needs a signed-in browser session against production

## Quarantine policy

Prefer cheap test fixes over `xfail`. If quarantined, mark `@pytest.mark.xfail(reason="...")` with an explicit reason and list it in the PR / CHANGELOG.
