# Production Deployment & Smoke Test Checklist

## Required Environment Variables (Production)
For a successful deployment in production (`ENVIRONMENT=production`), the following environment variables MUST be configured in your hosting environment (e.g., Render Dashboard):

- `ENVIRONMENT=production`
- `JWT_SECRET_KEY` (Must be a secure, random string)
- `DATABASE_URL` (Often populated automatically by Render PostgreSQL)
- `STRIPE_SECRET_KEY` (Your live Stripe secret key: `sk_live_...`)
- `STRIPE_WEBHOOK_SECRET` (Webhook signing secret: `whsec_...`)
- `FRONTEND_URL` (The public URL of the application)
- `ALLOWED_ORIGINS` (CORS origins, comma-separated if multiple)
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` (Required for AI compliance audits)
- `SHOW_DOCS=false` (Optional: defaults to false automatically when in production)

**Stripe Prices**
Ensure all Stripe Price IDs used by the application are provided:
- `STRIPE_PRICE_PERMIT_FILING`
- Additional pricing tiers if used (e.g., `STRIPE_PRICE_BASIC`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_PREMIUM`, `STRIPE_PRICE_STARTER`, `STRIPE_PRICE_GROWTH`, `STRIPE_PRICE_COMPLIANCE_ESSENTIALS`)

## Stripe Webhook Configuration
In your Stripe Developer Dashboard, you must register the following webhook endpoints to point to your live domain:
- `POST /api/subscriptions/webhook`
- `POST /api/v1/billing/webhooks`

## Smoke Tests (Post-Deploy)
Perform the following tests after deploying to verify that the launch-hardening mechanisms are active:

1. **Auth Check**: Register and login. Verify that the `access_token` cookie is set and has the `Secure` attribute (because the app is in production).
2. **Dashboard**: Verify the main dashboard loads successfully.
3. **Database Persistence**: Add a test property. Trigger a manual redeploy in Render. Verify the property still exists (confirming the `DELETE FROM properties` bug is fixed).
4. **Billing Flow**: Click a checkout link for a permit or subscription. Verify that it directs you to a real Stripe Checkout URL (and does not fallback to `/checkout-mock`).
5. **Webhook Processing**: Complete a test payment (if using test mode) or use the Stripe CLI to trigger an event, and verify the webhook activates the subscription.
6. **Compliance Fallback**: Attempt a compliance audit without providing a valid `GEMINI_API_KEY` in the environment. Verify the `eligibility_status` returns "Pending" and displays the legal disclaimer (not "Compliant").
7. **Documentation Security**: Visit `/docs`. Verify that it returns a 404 (not publicly available) unless you explicitly set `SHOW_DOCS=true`.
8. **Mock Checkout Security**: Visit `/checkout-mock`. Verify that it redirects away (e.g., to `/pricing`) and does not load the mock page.
