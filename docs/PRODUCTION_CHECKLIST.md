# Hosteva Production Deployment Checklist

This document serves as the final smoke-test checklist and environment reference for deploying Hosteva to production.

## 1. Required Environment Variables

When `ENVIRONMENT=production`, the application fail-closes many development mock behaviors (like mock checkouts, unsafe cookies, public API docs, and fake properties). The following variables MUST be set in the production environment (e.g. Render dashboard):

```bash
# Core
ENVIRONMENT=production
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your_secure_random_string
FRONTEND_URL=https://your-production-domain.com
ALLOWED_ORIGINS=https://your-production-domain.com

# Stripe Integration
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_PREMIUM=price_...
STRIPE_PRICE_PERMIT_FILING=price_...

# Third-Party APIs
GEMINI_API_KEY=your_google_ai_key
# OR GOOGLE_API_KEY=your_google_ai_key
```

### Optional overrides
- `SHOW_DOCS=true` (If you explicitly want `/docs` available in production. By default, it is disabled in production).

## 2. Stripe Webhook Configuration

In the Stripe Dashboard, you must configure a webhook endpoint pointing to your production URL:

- **Endpoint:** `https://your-production-domain.com/api/v1/billing/webhooks`
- **Events to listen for:**
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`

*Note: The older `https://your-production-domain.com/api/subscriptions/webhook` is also present for legacy routes, but it is recommended to use the `v1/billing` webhook.*

## 3. Post-Deployment Smoke Tests

After deploying to production, perform these manual verifications to ensure all environments switches engaged correctly:

1. **Authentication & Cookies:** Register a test account and log in. Inspect the `access_token` cookie. It MUST have `Secure=true`, `HttpOnly=true`, and `SameSite=lax`.
2. **Docs Lockdown:** Navigate to `/docs` and `/redoc`. These should return a `404 Not Found`.
3. **Property Data:** Navigate to the Dashboard. The properties list should be empty or reflect actual DB data (no more "123 Ocean Drive" mock data).
4. **Billing Failure:** Attempt to click a pricing tier on the `/pricing` page (without setting real Stripe keys first) or check out a permit. You should see a safe `502 Payment provider unavailable` or `500 Billing not configured` error, rather than a successful mock checkout.
5. **Real Billing:** Add live Stripe keys and a valid Price ID. Verify you are redirected to a real Stripe Checkout session (not a local mock).
6. **Compliance Search:** Go to the Compliance page and search for "Florida". The "Florida State (Sample)" mock ordinance should no longer appear in the search results.

## 4. Troubleshooting
- If checkout redirects to `/checkout-mock` in production, check that `ENVIRONMENT` is exactly `production` (case-insensitive).
- If you receive `403 Forbidden` on compliance routes, it's expected for some mock seeding endpoints like `/api/compliance/seed-miami` which are disabled in production.

## Billing kill-switch (P0 — 2026-09-05)

`BILLING_ENABLED` defaults to **false**. Until auth-bound Stripe ships, Checkout Session creation returns **503 Billing temporarily unavailable** on:
- `POST /api/subscriptions/checkout`
- `POST /api/v1/billing/checkout`
- legacy `POST .../create-checkout-session`

Do **not** set `BILLING_ENABLED=true` in production until checkout requires a real Host id (never `user_mock_123`) and is verified.
