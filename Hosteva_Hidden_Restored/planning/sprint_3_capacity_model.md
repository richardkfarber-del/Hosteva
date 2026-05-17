# Sprint 3, Phase 2: Consensus & Capacity Check (The War Room)

## 1. Complexity Assessment
Sprint 3 ("The Value Delivery") involves high-risk, high-complexity components:
*   **External Integrations:** Airbnb & VRBO APIs (complex JSON payloads, pricing/availability matrices).
*   **Security:** OAuth2 token lifecycle management (secure storage, refresh logic).
*   **Architecture:** Asynchronous task routing (e.g., Celery/Redis), rate limiting, and retry mechanics.
*   **Data Modeling:** 1-to-many DB schemas (`property_listings`), complex state management.
*   **Generation:** Dynamic DBPR form mapping and auto-fill.

## 2. Compute & Token Cost Modeling
Given the requirement to adhere strictly to the API Contract Mandate and manage deep context across async workers:
*   **Context Window (Tokens In):** Heavy. Agents will need to ingest external API structures, existing DB schemas, and async configurations. (Est. 100k - 150k input tokens per major task iteration).
*   **Generation (Tokens Out):** Significant output required for backend schemas, async worker functions, and rigorous `pytest` mock suites. (Est. 10k - 25k output tokens per task iteration).
*   **Cost Implication:** High compute cost, but necessary due to failure risks in OAuth, data leaks, and Async flows.

## 3. Model Recommendations (Phase 3: The Gauntlet)
We must evaluate local (`qwen2.5-coder:7b`) vs. cloud (`google/gemini-3-pro`).

**Analysis of Local Model (`qwen2.5-coder:7b`):**
While `qwen2.5-coder:7b` is excellent for isolated logic and simple CRUD, it lacks the parameter depth to reliably handle multi-system orchestration, OAuth state tracking, and complex asynchronous architectural design without hallucinating API contracts or dropping context. Relying on a 7B model for intricate Airbnb/VRBO API integration poses a severe risk to Sprint 3's success.

**Recommendation: DEPLOY CLOUD (`google/gemini-3-pro`)**
*   **Makers (Wasp, Shang-Chi, Hulk):** Must be routed to `google/gemini-3-pro`. The architectural spikes (TCK-301) and async task queue implementations (TCK-303) demand superior reasoning, deep context retention, and strict adherence to defined JSON payloads.
*   **QA (Black Widow, Cap):** Must be routed to `google/gemini-3-pro`. Mocking 3rd-party OAuth flows and asynchronous workers in `pytest` requires a deep understanding of the generated backend contracts.

**Conclusion:** 
Phase 3 of Sprint 3 requires high-tier reasoning. Local 7B models lack the capacity for this specific workload. I recommend routing all Makers and QA to `google/gemini-3-pro` to ensure robust, secure delivery of the Value Delivery sprint.