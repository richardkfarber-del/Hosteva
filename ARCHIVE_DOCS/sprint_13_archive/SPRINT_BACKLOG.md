# SPRINT BACKLOG

## FEAT-013: Stripe Paywall Integration

**Ticket 1:** DBA - Implement Database Schema for Payments and Subscriptions
**Files to Modify:**
- `/migrations/versions/xxxx_add_payment_tables.py` (Create new file)

*   **Story:** As a Database Administrator, I need to create the necessary tables and types to support Stripe products, prices, and user subscriptions, so that the application can accurately track customer entitlements and payment status.

*   **Gherkin:**
    ```gherkin
    Feature: Database Schema for Payments
      In order to sell products and manage subscriptions
      As a backend system
      I need persistent storage for payment-related entities.

      Scenario: Create payment and subscription tables
        Given a clean database schema
        When the migration script is run
        Then the following tables must exist: "products", "prices", "subscriptions"
        And the "users" table must have a new nullable column "stripe_customer_id" with a unique index
        And a new ENUM type "subscription_status" with values ('active', 'trialing', 'past_due', 'canceled', 'unpaid') must be created
        And all foreign key constraints must be correctly established between the tables.
    ```

*   **Acceptance Criteria:**
    1.  A new database migration script is created.
    2.  When the migration is applied, a `products` table is created with the exact schema defined in the Spike Research Artifact (id, stripe_product_id, name, description, is_active, created_at, updated_at).
    3.  When the migration is applied, a `prices` table is created with the exact schema defined in the Spike Research Artifact (id, stripe_price_id, product_id, is_active, type, unit_amount, currency, created_at, updated_at).
    4.  When the migration is applied, a `subscriptions` table is created with the exact schema defined in the Spike Research Artifact, including the `subscription_status` ENUM type.
    5.  When the migration is applied, the `users` table is altered to add a `stripe_customer_id` column (VARCHAR(255), UNIQUE).
    6.  An index is created on `users.stripe_customer_id`.
    7.  All specified foreign key relationships (`prices.product_id` -> `products.id`, `subscriptions.user_id` -> `users.id`, `subscriptions.product_id` -> `products.id`) are implemented.
    8.  The migration script must include a downgrade path that correctly removes all new tables, columns, and types.

---

**Ticket 2:** BE-Engineer - Create Stripe Checkout Session Endpoint
**Files to Modify:**
- `/src/api/v1/payments/routes.py` (Create new file)
- `/src/api/v1/payments/service.py` (Create new file)

*   **Story:** As a Backend Engineer, I need to create a secure endpoint that generates a Stripe Checkout session for a user, so they can be redirected to Stripe to complete their purchase.

*   **Gherkin:**
    ```gherkin
    Feature: Stripe Checkout Session Creation
      In order to initiate a payment
      As a user
      I need the system to generate a secure Stripe Checkout session.

      Scenario: Authenticated user requests a checkout session for a subscription
        Given I am an authenticated user with user_id "user-123"
        And a valid "Hosteva Pro" product with price_id "price_abc" exists
        When I send a POST request to "/api/v1/payments/create-checkout-session" with the price_id "price_abc"
        Then the system should return a 200 OK status
        And the response body must contain a JSON object with a "redirectUrl" key
        And the Stripe API must have been called to create a session with mode='subscription', client_reference_id='user-123', and the correct success/cancel URLs.

      Scenario: Unauthenticated user attempts to create a session
        Given I am not an authenticated user
        When I send a POST request to "/api/v1/payments/create-checkout-session"
        Then the system should return a 401 Unauthorized status.

      Scenario: Request with an invalid price_id
        Given I am an authenticated user
        When I send a POST request to "/api/v1/payments/create-checkout-session" with an invalid price_id "price_invalid"
        Then the system should return a 404 Not Found status.
    ```

*   **Acceptance Criteria:**
    1.  A new endpoint `POST /api/v1/payments/create-checkout-session` is created.
    2.  The endpoint must require user authentication. Unauthenticated requests must be rejected with a 401 status.
    3.  The endpoint accepts a JSON payload containing a `price_id`.
    4.  The service validates that the `price_id` exists in the `prices` database table. If not found, it returns a 404 error.
    5.  The service calls the Stripe API to create a new Checkout Session.
    6.  The `client_reference_id` parameter sent to Stripe MUST be populated with the authenticated user's internal `user_id`.
    7.  The `mode` parameter is set to `'subscription'`.
    8.  The `success_url` is set to `https://hosteva.com/payment-success?session_id={{CHECKOUT_SESSION_ID}}`.
    9.  The `cancel_url` is set to `https://hosteva.com/payment-cancelled`.
    10. Upon a successful response from Stripe, the endpoint returns a JSON object `{ "redirectUrl": "session.url_from_stripe" }` with a 200 status.
    11. Stripe API keys must be loaded from environment variables/secrets management, not hardcoded.

---

**Ticket 3:** BE-Engineer - Implement Stripe Webhook Handler for Provisioning
**Files to Modify:**
- `/src/api/v1/webhooks/stripe_handler.py` (Create new file)

*   **Story:** As a Backend Engineer, I need to create a robust webhook handler to listen for events from Stripe, so that I can reliably update a user's subscription status and grant or revoke access to features.

*   **Gherkin:**
    ```gherkin
    Feature: Stripe Webhook Processing
      To ensure user access is managed correctly based on payment status
      As the system
      I must process incoming webhook events from Stripe securely and reliably.

      Scenario: Successful checkout session completion
        Given a user with user_id "user-123" has completed a Stripe checkout
        When Stripe sends a "checkout.session.completed" event to "/api/v1/webhooks/stripe" with a valid signature and client_reference_id "user-123"
        Then the webhook handler must verify the signature
        And it must create a new record in the "subscriptions" table for "user-123" with status 'active'
        And it must update the "users" table to set the "stripe_customer_id" for "user-123"
        And it must return a 200 OK status to Stripe.

      Scenario: Subscription cancellation
        Given a user with an active subscription "sub_xyz"
        When Stripe sends a "customer.subscription.deleted" event for "sub_xyz"
        Then the webhook handler must verify the signature
        And update the corresponding record in the "subscriptions" table to set its status to 'canceled'
        And return a 200 OK status.

      Scenario: Webhook with an invalid signature
        Given any Stripe event payload
        When the event is sent to "/api/v1/webhooks/stripe" with an invalid "Stripe-Signature" header
        Then the handler must immediately return a 400 Bad Request status
        And no database changes should be made.

      Scenario: Processing a duplicate event
        Given a Stripe event with id "evt_123" has already been processed successfully
        When the same event with id "evt_123" is received again
        Then the handler must verify the signature
        And recognize the event has been processed
        And return a 200 OK status immediately without performing any database operations.
    ```

*   **Acceptance Criteria:**
    1.  A new endpoint `POST /api/v1/webhooks/stripe` is created.
    2.  The handler MUST verify the `Stripe-Signature` header of every incoming request using the configured webhook signing secret. Requests with an invalid signature must be rejected with a 400 status.
    3.  The handler implements an idempotency check (e.g., logging processed `event.id`s) to prevent double-provisioning from webhook retries.
    4.  On a `checkout.session.completed` event, the handler extracts the `client_reference_id` (our `user_id`), creates/updates the `stripe_customer_id` on the `users` record, and creates a new `subscriptions` record with the details from the event payload.
    5.  The handler correctly processes `customer.subscription.deleted` events by updating the status of the relevant subscription in the database.
    6.  The handler correctly processes `invoice.payment_failed` events by updating the status of the relevant subscription to `past_due`.
    7.  The handler correctly processes `invoice.payment_succeeded` events by updating the `current_period_start` and `current_period_end` for the relevant subscription and ensuring its status is `active`.
    8.  The handler must return a `200 OK` status to Stripe for all successfully processed events (including duplicates).

---

**Ticket 4:** BE-Engineer - Implement Route Protection Middleware
**Files to Modify:**
- `/src/middleware/auth.py` (Modify existing or create new file)
- `/src/api/v1/dashboard/routes.py` (Modify existing or create new file)

*   **Story:** As a Backend Engineer, I need to protect the `/host-dashboard` route so that only users with an active subscription can access it, ensuring our paywall is enforced.

*   **Gherkin:**
    ```gherkin
    Feature: Paywall Route Protection
      To enforce the business model
      As the system
      I must prevent non-paying users from accessing premium content.

      Scenario: User with an active subscription accesses the dashboard
        Given I am an authenticated user with an 'active' subscription in the database
        When I make a request to an endpoint under "/host-dashboard"
        Then the request should be allowed and I receive a 200 OK status.

      Scenario: User without any subscription accesses the dashboard
        Given I am an authenticated user with no subscription record in the database
        When I make a request to an endpoint under "/host-dashboard"
        Then the request should be denied and I receive a 403 Forbidden status.

      Scenario: User with a 'past_due' or 'canceled' subscription accesses the dashboard
        Given I am an authenticated user with a 'past_due' subscription
        When I make a request to an endpoint under "/host-dashboard"
        Then the request should be denied and I receive a 403 Forbidden status.
    ```

*   **Acceptance Criteria:**
    1.  A middleware or decorator is created that checks the subscription status of the authenticated user.
    2.  The middleware queries the `subscriptions` table for the current user.
    3.  Access is granted ONLY if the user has a subscription record with `status = 'active'`.
    4.  Access is denied with a 403 Forbidden status for users with no subscription, or subscriptions with statuses like `past_due`, `canceled`, or `unpaid`.
    5.  This protection logic is applied to all routes beginning with `/host-dashboard`.

---

**Ticket 5:** FE-Engineer - Build Foundational UI Atoms
**Files to Modify:**
- `/src/components/atoms/Button.atom.jsx` (Create new file)
- `/src/components/atoms/Input.atom.jsx` (Create new file)
- `/src/components/atoms/Typography.atom.jsx` (Create new file)
- `/src/components/atoms/Icon.atom.jsx` (Create new file)
- `/src/components/atoms/Spinner.atom.jsx` (Create new file)

*   **Story:** As a Frontend Engineer, I need to create the basic, reusable atomic components for the paywall modal, so that we have a consistent and maintainable design system.

*   **Gherkin:**
    ```gherkin
    Feature: UI Atom Creation
      To ensure a consistent and reusable UI
      As a developer
      I need a set of basic, stateless UI components.

      Scenario: Render a primary button in a loading state
        Given the "Button.atom.jsx" component
        When I render it with props `isLoading={true}` and children "Pay"
        Then the component should render a <button> element
        And the button must be disabled
        And the button must display a "Spinner.atom.jsx" component instead of the text "Pay".
    ```

*   **Acceptance Criteria:**
    1.  A `Button.atom.jsx` component is created that accepts `variant`, `size`, `isLoading`, and `isDisabled` props as described in the UI/UX research.
    2.  An `Input.atom.jsx` component is created that accepts `label`, `placeholder`, `type`, and `error` props.
    3.  A `Typography.atom.jsx` component is created that accepts `as` and `variant` props.
    4.  An `Icon.atom.jsx` component is created that can render SVG icons for at least 'lock' and 'checkmark'.
    5.  A `Spinner.atom.jsx` component is created that renders a CSS-based loading animation.
    6.  All components must be stateless and receive their data via props. No styling work included in this scope beyond basic structure, unless styles are provided in UI mockups.

---

**Ticket 6:** FE-Engineer - Build Paywall Modal Organism
**Files to Modify:**
- `/src/components/molecules/FeatureListItem.molecule.jsx` (Create new file)
- `/src/components/organisms/PaywallModal.organism.jsx` (Create new file)

*   **Story:** As a Frontend Engineer, I need to assemble the `PaywallModal` component using the atoms and molecules, and integrate Stripe Elements for secure payment input, to create the core user-facing checkout experience.

*   **Gherkin:**
    ```gherkin
    Feature: Paywall Modal
      To allow users to purchase a subscription
      As a Frontend Application
      I must display a modal with a secure payment form.

      Scenario: User opens the paywall modal
        Given a user is viewing a page with a locked feature
        When the user clicks the "Unlock" button
        Then the "PaywallModal.organism.jsx" component should be rendered as a visible overlay
        And the modal must display the productName, price, and features passed in as props
        And the Stripe CardElement must be rendered within the form.

      Scenario: User attempts payment with invalid card details
        Given the Paywall Modal is open
        When the user enters invalid card details and clicks "Pay and Unlock"
        Then the "Pay and Unlock" button should enter a loading state
        And an error message from Stripe (e.g., "Your card number is invalid.") must be displayed within the modal
        And the button should return to its active state.

      Scenario: User successfully completes payment
        Given the Paywall Modal is open with valid card details entered
        When the user clicks "Pay and Unlock" and the backend confirms success
        Then the modal content is replaced with a success message and checkmark icon
        And after a 2-second delay, the modal automatically closes.
    ```

*   **Acceptance Criteria:**
    1.  A `FeatureListItem.molecule.jsx` is created as described in the UI/UX research.
    2.  A `PaywallModal.organism.jsx` is created that matches the structure in the UI/UX implementation sketch.
    3.  The modal receives `isOpen`, `onClose`, `productName`, `price`, `priceDescription`, and `features` as props to ensure reusability.
    4.  Stripe Elements is integrated to render the `CardElement` for secure credit card input.
    5.  On form submission, the component calls the `POST /api/v1/payments/create-checkout-session` endpoint created in Ticket 2.
    6.  Upon receiving a `redirectUrl` from the backend, the frontend redirects the user to the Stripe Checkout page.
    7.  The modal displays error messages returned from the Stripe API (e.g., card declined) within the modal UI.
    8.  The primary CTA button shows a loading state (`isLoading={true}`) during the API call.
    9.  The modal includes the mandatory legal compliance UI elements from the Ethics audit: transparent pricing, "Powered by Stripe" text, and a secure lock icon.

---

**Ticket 7:** FE-Engineer - Implement Frontend Route Guard and User Flow
**Files to Modify:**
- `/src/App.js` or `/src/routes.js` (Modify existing file)
- `/src/components/utilities/RouteGuard.jsx` (Create new file)
- `/src/pages/HostDashboardPage.jsx` (Modify existing or create new file)
- `/src/pages/PaymentSuccessPage.jsx` (Create new file)
- `/src/pages/PaymentCancelledPage.jsx` (Create new file)

*   **Story:** As a Frontend Engineer, I need to protect the `/host-dashboard` client-side route and manage the user flow for payments, so that non-paying users are prompted to subscribe and users are shown appropriate confirmation pages after payment attempts.

*   **Gherkin:**
    ```gherkin
    Feature: Frontend Access Control and Payment Flow
      To provide a seamless user experience for the paywall
      As a user
      I want to be redirected to pay if I try to access premium content without a subscription.

      Scenario: Non-subscribed user navigates to the dashboard
        Given I am a logged-in user with no active subscription
        When I attempt to navigate directly to "/host-dashboard"
        Then I am redirected to the page where I can initiate the purchase flow (e.g., a pricing page or the homepage with the paywall modal triggered).

      Scenario: Subscribed user navigates to the dashboard
        Given I am a logged-in user with an active subscription
        When I attempt to navigate directly to "/host-dashboard"
        Then I am shown the content of the "HostDashboardPage.jsx" component.

      Scenario: User returns after a successful payment
        Given I have completed a payment on Stripe Checkout
        When I am redirected back to "/payment-success"
        Then I see a page confirming my payment was successful and my access has been granted.

      Scenario: User cancels the payment process
        Given I am on the Stripe Checkout page
        When I click the back button or cancel the payment
        Then I am redirected back to "/payment-cancelled"
        And I see a page indicating the payment was not completed.
    ```

*   **Acceptance Criteria:**
    1.  A client-side route guard component (`RouteGuard.jsx`) is created.
    2.  This guard checks the user's subscription status (from a global state like Redux/Zustand, which is populated on login).
    3.  If a user without an active subscription tries to access `/host-dashboard`, they are redirected.
    4.  If a user with an active subscription tries to access `/host-dashboard`, the component renders.
    5.  A new page component `PaymentSuccessPage.jsx` is created and mapped to the `/payment-success` route. It displays a simple success message.
    6.  A new page component `PaymentCancelledPage.jsx` is created and mapped to the `/payment-cancelled` route. It displays a message that the payment was cancelled.

---

**Ticket 8:** Legal-Tech - Update ToS and Privacy Policy Pages
**Files to Modify:**
- `/src/pages/TermsOfService.jsx` (Modify existing or create new file)
- `/src/pages/PrivacyPolicy.jsx` (Modify existing or create new file)
- `/src/components/organisms/PaywallModal.organism.jsx` (Modify existing file)

*   **Story:** As a Product Manager, I need to ensure our legal documents and checkout UI are updated with mandatory disclaimers and clauses, to mitigate legal risk and comply with Stripe's terms.

*   **Gherkin:**
    ```gherkin
    Feature: Legal Compliance for Payments
      To protect the business and inform users
      As the company
      We must have clear legal terms regarding payments and service use.

      Scenario: User views the Terms of Service
        Given a user navigates to the "/terms-of-service" page
        When the page content is rendered
        Then it must contain clauses for "Payment, Subscription, and Cancellation", a "Refund Policy", the "Not Legal Advice" disclaimer, and "Limitation of Liability", using the language specified in the legal audit memo.

      Scenario: User views the Privacy Policy
        Given a user navigates to the "/privacy-policy" page
        When the page content is rendered
        Then it must explicitly name Stripe as a third-party data processor for payments.

      Scenario: User is presented with the checkout modal
        Given the Paywall Modal is open
        When the user views the form
        Then an unticked checkbox must be present with the text "I have read and agree to the Hosteva Terms of Service and Privacy Policy."
        And the "Terms of Service" and "Privacy Policy" text must be hyperlinks to the respective pages
        And the primary "Pay and Unlock" button must be disabled until the checkbox is ticked.
    ```

*   **Acceptance Criteria:**
    1.  The content of the `/src/pages/TermsOfService.jsx` component is updated to include all four mandatory clauses specified in the legal audit memo. **NOTE:** We do not yet have terms of service or a privacy policy. These updates will be the FIRST entries in our terms of service and privacy policy. As the project progresses and we add to them, we will clean up the documents themselves. But for now, these will be the first entries we have documented.
    2.  The content of the `/src/pages/PrivacyPolicy.jsx` component is updated to name Stripe as a third-party payment processor. **NOTE:** See note in criterion 1 regarding this being the first entry.
    3.  The `PaywallModal.organism.jsx` is modified to include an unticked checkbox for ToS and Privacy Policy agreement.
    4.  The checkbox text must contain hyperlinks to `/terms-of-service` and `/privacy-policy`.
    5.  The main payment submission button in the modal is disabled if the agreement checkbox is not checked.
