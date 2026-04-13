# Spike: Airbnb & VRBO Architecture Blueprint (TCK-301)

## 1. Authentication Flows (OAuth2)
Both Airbnb and VRBO (Expedia Group) utilize standard OAuth 2.0 authorization code flows for partner API access.
*   **Authorization Request:** The Hosteva user initiates the connection. We redirect them to the platform's authorization endpoint, passing our `client_id`, `redirect_uri`, and requested `scopes` (e.g., `listings_write`, `reservations_read`).
*   **Consent & Callback:** The user logs into their platform account, approves Hosteva, and is redirected back to our `redirect_uri` with an authorization `code`.
*   **Token Exchange:** Hosteva's backend exchanges the `code` for an `access_token` and `refresh_token` via the platform's token endpoint (using basic auth with `client_id` and `client_secret`).
*   **Usage:** The `access_token` is passed as a Bearer token (`Authorization: Bearer <token>`) in the headers of all subsequent API calls.
*   **Token Refresh:** A background worker monitors token expiry. When the `access_token` nears expiration (usually after 1-2 hours), the worker uses the `refresh_token` to fetch a new pair, ensuring uninterrupted async operations.

## 2. Database Architecture

### 2.1 OAuth Token Storage Schema
We require a secure, encrypted table to store the tokens per user per platform.

```sql
CREATE TABLE oauth_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'airbnb', 'vrbo'
    platform_account_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL, -- Encrypted at rest
    refresh_token TEXT NOT NULL, -- Encrypted at rest
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    scopes TEXT[],
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'revoked', 'expired'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, platform, platform_account_id)
);
```

### 2.2 Property Listings (1-to-Many Schema)
A single Hosteva property can be listed on multiple OTAs. We need a table to track these external deployments.

```sql
CREATE TABLE property_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    platform_name VARCHAR(50) NOT NULL, -- 'airbnb', 'vrbo'
    external_listing_id VARCHAR(255), -- The ID returned by the platform
    external_url TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'active', 'failed', 'unlist'
    sync_status VARCHAR(50) DEFAULT 'in_sync', -- 'in_sync', 'syncing', 'error'
    last_sync_at TIMESTAMP WITH TIME ZONE,
    error_log JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(property_id, platform_name)
);
```

## 3. Asynchronous Task Queue Mechanics (Redis/Celery)
Given the potential for slow API responses, rate limits, and network errors, all interactions with external platforms must be decoupled from the main HTTP request-response cycle.

*   **Stack:** Python Celery with Redis as the broker and result backend.
*   **Task Dispatch:** When a user completes the listing generation module (TCK-303), the backend saves the generated data and enqueues a task: `sync_property_to_otas.delay(property_id)`.
*   **Task Workers:** Celery workers pick up the task, load the property data, format the specific JSON payloads, load the valid OAuth tokens, and execute the API requests.
*   **Rate Limiting & Retries:** Tasks will be configured with exponential backoff for 429 (Too Many Requests) and 5xx (Server Error) responses. E.g., `@app.task(bind=True, max_retries=5, default_retry_delay=60)`.
*   **State Updates:** The worker updates the `sync_status` and `error_log` in the `property_listings` table. Upon success, it writes the `external_listing_id`.

## 4. Endpoints & The API Contract Mandate
*   **Airbnb Create Listing Endpoint (Conceptual Partner API):** `POST /v2/listings`
*   **VRBO Create Listing Endpoint (Expedia Connectivity API):** `POST /v3/properties`

The exact expected JSON payload contracts, dictating pricing, photos, and availability structures, have been extracted and written to `/home/rdogen/.openclaw/workspace-the-hulk/Hosteva/state.json` per the LOBSTER protocol.