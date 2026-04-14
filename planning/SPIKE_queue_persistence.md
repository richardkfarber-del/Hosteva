# SPIKE: Queue Persistence & Async Alternatives
**Assignee:** The Hulk (R&D Scientist)
**Objective:** Analyze the removal of Celery and identify lightweight, persistent alternatives for the async queue that survive server crashes without bloating infrastructure.

## 1. Analysis: Why Celery Was Removed
Based on the current environment and constraints, Celery was removed due to the following structural issues:
* **Infrastructure Costs (Redis/RabbitMQ):** Celery requires a dedicated message broker (usually Redis or RabbitMQ). Hosting a highly available Redis instance adds unacceptable monthly infrastructure costs to a lean startup environment.
* **Memory Limits on Render:** Celery workers are heavy and consume significant RAM. Render's lower-tier instances (often 512MB or 1GB) would frequently face Out-Of-Memory (OOM) kills when running both the web server and the Celery worker concurrently.
* **Deployment Complexity:** Managing separate worker dynos/services, ensuring broker connectivity, and dealing with orphaned tasks adds unnecessary DevOps overhead.

## 2. Alternatives Investigated
To replace Celery, we need a solution that is lightweight, uses the existing PostgreSQL database for persistence (avoiding new infrastructure), and survives server crashes.

### Option A: `arq` (Redis-backed, but lightweight)
* **Pros:** Built for `asyncio`, much lighter than Celery.
* **Cons:** Still requires Redis, which defeats the goal of removing Redis infrastructure costs. **Rejected.**

### Option B: `TaskIQ`
* **Pros:** Highly modular, supports async natively, and has plugins for various brokers.
* **Cons:** While it can use alternative brokers, configuring it strictly for PostgreSQL without polling overhead can be complex.

### Option C: PostgreSQL-Backed Queues (e.g., `Procrastinate` or Simple DB Polling)
* **Pros:** Uses the existing PostgreSQL database. Zero additional infrastructure costs. Fully persistent (if the server crashes, the job remains in the DB).
* **Cons:** Polling the DB can introduce slight latency compared to Redis Pub/Sub.
* **Mechanism:** 
  - A `jobs` table with statuses (`PENDING`, `RUNNING`, `FAILED`, `COMPLETED`).
  - Use Postgres `SKIP LOCKED` in queries so concurrent workers don't pick up the same job.
  - Can be implemented via a lightweight library like `Procrastinate` or custom `asyncio` polling workers within the main FastAPI loop.

## 3. Hulk's Recommendation
**Implement a PostgreSQL-backed queue.**
Given the tight memory limits on Render and the mandate to reduce infrastructure costs, the existing Postgres DB should act as the message broker. 
* **Implementation:** Use a library like `Procrastinate` or write a minimal async worker using `SELECT ... FOR UPDATE SKIP LOCKED`. 
* **Impact:** This ensures jobs (like email sending or data syncs) are never lost during a deployment or OOM crash, while keeping the architecture lean and cost-effective.
