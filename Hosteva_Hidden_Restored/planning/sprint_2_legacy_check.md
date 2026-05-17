# Sprint 2 Phase 2: Legacy Testing Check & Migration Risk Assessment

## 1. Required Legacy Characterization Tests
Before implementing the new schemas, the following legacy characterization tests are required to ensure existing behaviors remain intact:
* **User Registration & Profile Creation:** Verify existing insert logic for user/property records functions without the new subscription and document columns.
* **Basic Application Workflows:** Ensure any existing authentication, property eligibility checks, and dashboard data retrieval queries execute correctly before schema modifications.
* **Database State Check:** Capture the current schema layout and sample data structure to establish a baseline.

## 2. Risk Assessment of Migrating SQLite
The introduction of `current_period_end`, Stripe webhook routes, and S3 integrations carries the following risks for the current SQLite database:
* **Additive Schema Changes (Low Risk):** The required database updates (`provider_customer_id`, `provider_subscription_id`, `current_period_end`, `subscription_status`, `file_url`, `document_type`, `generated_at`) are additive. SQLite supports `ALTER TABLE ADD COLUMN`, making this migration straightforward. 
* **Data Integrity (Medium Risk):** Existing user records will have NULL or missing values for the new columns. Migration scripts must handle default values gracefully (e.g., setting legacy users' `subscription_status` to a default 'free' or 'inactive' state).
* **Concurrency (High Risk):** SQLite is typically synchronous and has limited write concurrency. The new architecture introduces async background workers (Redis) and async Webhook payment processing. Multiple concurrent writes from webhooks and background workers might hit database locking issues (`database is locked` errors). This is the highest risk of keeping SQLite while adding async distributed processing components. Migration to PostgreSQL might be required if concurrency becomes an issue.

## Conclusion
Legacy characterization tests should focus on preserving the current read/write functionality of user and property records. While the schema migration itself is low risk, the introduction of asynchronous workers and webhooks introduces high concurrency risks for SQLite.
