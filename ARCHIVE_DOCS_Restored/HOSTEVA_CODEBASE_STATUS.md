# Hosteva Codebase Status & Bug Prioritization

## 1. Stripe Webhook Failure (Critical - Revenue Blocker)
- **Issue:** The Stripe webhook successfully catches payment events, but the database logic to activate the user's subscription is commented out.
- **Location:** `app/routers/stripe.py` (and duplicate files).

## 2. Missing Authentication Flow (Critical - Access Blocker)
- **Issue:** The `/login` route is missing entirely. We have a `ProtectedRoute.js` component, but no way for users to actually log in and get a session token.
- **Location:** Flagged as unbuilt (FEAT-019).

## 3. Dashboard Template Literal Leak [BUG-001] (High - UI Blocker)
- **Issue:** Raw JavaScript code is leaking and rendering as plain text underneath the map on the host dashboard.
- **Location:** `templates/dashboard.html`.

## 4. Dashboard CSS Duplication [BUG-003] (Medium - Tech Debt)
- **Issue:** CSS duplication is bloating the page and causing styling conflicts on the dashboard.
- **Location:** `templates/dashboard.html` and associated stylesheets.
