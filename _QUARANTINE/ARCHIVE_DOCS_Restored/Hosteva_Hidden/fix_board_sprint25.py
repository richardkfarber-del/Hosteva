content = """

# Sprint 25 Backlog: SPIKE-017 (pgvector Memory Migration)

## Phase 1: Infrastructure

**CHORE-034: Add pgvector to Docker Compose**
* **Acceptance Criteria:**
  - `docker-compose.yml` includes a new service using the official `pgvector/pgvector:pg16` image.
  - Persistent volume is defined for the database data.
  - Default ports (5432) are mapped and accessible locally.

**CHORE-035: Initialize pgvector Extension**
* **Acceptance Criteria:**
  - An initialization SQL script (e.g., `01-init-pgvector.sql`) is created in the Docker entrypoint directory.
  - The script executes `CREATE EXTENSION IF NOT EXISTS vector;`.

**CHORE-036: Define Embeddings Table Schema**
* **Acceptance Criteria:**
  - A migration SQL script is created to define the `agent_memories` table.
  - Table includes columns: `id` (UUID), `agent_id` (varchar), `content` (text), `metadata` (jsonb), and `embedding` (vector).
  - An HNSW index is applied to the `embedding` column for optimized similarity search.

**CHORE-037: Deploy mcp-server-postgres**
* **Acceptance Criteria:**
  - `mcp-server-postgres` is added as a service to `docker-compose.yml`.
  - It is configured to wait for the pgvector service to be healthy before starting.

**CHORE-038: Configure MCP Environment Variables**
* **Acceptance Criteria:**
  - Database connection strings are securely passed to `mcp-server-postgres` via `.env`.
  - Connection logs verify a successful handshake with the pgvector database on startup.

## Phase 2: Migration Scripting

**CHORE-039: Python Script Scaffolding for MEMORY.md**
* **Acceptance Criteria:**
  - A Python script `memory_migrator.py` is created.
  - Script successfully opens, reads, and closes a target `MEMORY.md` file natively in WSL2.

**CHORE-040: Implement Semantic Chunking Logic**
* **Acceptance Criteria:**
  - The Python script parses the markdown file and splits it into logical chunks (by headers or bullet points).
  - Each chunk retains the context of its parent header as a metadata dictionary object.

**CHORE-041: Integrate Ollama nomic-embed-text API**
* **Acceptance Criteria:**
  - The script sends a chunked text string to the local Ollama API (`/api/embeddings`).
  - Model parameter is strictly set to `nomic-embed-text`.
  - The script successfully receives and validates a floating-point array response.

**CHORE-042: Seed Metadata and Vectors into pgvector**
* **Acceptance Criteria:**
  - The Python script connects to the local pgvector instance (via `psycopg2` or `asyncpg`).
  - It iterates over all semantic chunks, fetches their embedding, and executes an `INSERT` statement.
  - The `metadata` JSONB column correctly reflects the agent owner and markdown header context.

## Phase 3: Reliability & The Dream Cycle

**CHORE-043: Implement Append-Only Short-Term Memory Log**
* **Acceptance Criteria:**
  - A utility function is created to append text to a `short_term_memory.jsonl` file.
  - File locking is implemented to prevent race conditions from concurrent agent writes.

**CHORE-044: Scaffold Dream Cycle Worker**
* **Acceptance Criteria:**
  - A Python script `dream_worker.py` is created.
  - It includes a listener that only activates when the FastAPI state machine registers the `DREAMSTATE_READY` pipeline state.

**CHORE-045: Dream Cycle Short-Term Queue Processing**
* **Acceptance Criteria:**
  - When `DREAMSTATE_READY` is triggered, the worker reads all entries from `short_term_memory.jsonl`.
  - It successfully parses the JSONL entries into memory objects.

**CHORE-046: Dream Cycle Vectorization and Hardcoding**
* **Acceptance Criteria:**
  - The worker generates embeddings for each short-term memory via Ollama.
  - It inserts the vectors and metadata into the `agent_memories` pgvector table.

**CHORE-047: Dream Cycle Log Wiping**
* **Acceptance Criteria:**
  - The worker verifies the database `INSERT` transactions were successful.
  - Only upon success, the worker truncates/clears `short_term_memory.jsonl` to reset the queue.

**CHORE-048: Establish CORE_MEMORY.md Fallback**
* **Acceptance Criteria:**
  - A static, minimal `CORE_MEMORY.md` file is defined for each agent.
  - The agent's memory retrieval logic wraps the pgvector MCP query in a `try/except` block.
  - If the database connection times out or fails, the logic falls back to reading `CORE_MEMORY.md` locally.

**CHORE-049: Vector DB Critical Outage Alerting**
* **Acceptance Criteria:**
  - The MCP client implementation must intercept any `ConnectionRefusedError`, `TimeoutError`, or `OperationalError` when attempting to connect to `pgvector`.
  - Upon catching a connection failure, the logic MUST instantly generate an atomic write to `/home/rdogen/OpenClaw_Factory/projects/Hosteva/CRITICAL_ALERT.txt`.
  - The alert MUST contain the timestamp, the agent ID attempting the connection, and the specific database error trace.
  - The Orchestrator's standard 5-minute heartbeat loop will intercept this `CRITICAL_ALERT.txt` file and push the notification directly to the Secretary and Director via Telegram.
"""

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md", "a") as f:
    f.write(content)
print("Sprint 25 appended to project_board.md")
