# Hosteva — Environment Preparation Checklist (GTM Launch Strategy Phase)

This document details the exact terminal initialization, database migration commands, and dependency installations that the Google Antigravity agent must execute before writing any application code for the 12-week GTM launch phase.

---

# 1\. Environment Verification & Startup

Before executing any commands, verify that your local development environment has the following baseline services active:

- **Python:** v3.12.0 or higher (`python3 --version`)  
- **Redis:** Running locally on port 6379 (`redis-cli ping` returns `PONG`)  
- **PostgreSQL:** Running and initialized with `pgvector` extension enabled.  
- **Stripe CLI:** Installed and authenticated locally (`stripe login` completed).

---

# 2\. Directory Verification

Ensure the following local folder paths are scaffolded and read/write accessible:

- **Root Repository Path:** `/working_dir/`  
- **Database Seed Directory:** `/working_dir/ops/`  
- **Configuration Directory:** `/working_dir/ops/`  
- **Documentation Path:** `/working_dir/docs/`

---

# 3\. Dependency Scaffolding Commands

Execute the following commands from the root repository directory to install the new packages required for vector databases, billing, document processing, and iCal parsing:

\# Activate the python virtual environment

source .venv/bin/activate

\# Install vector, billing, scraping, and iCal parsing packages

uv pip install pgvector stripe beautifulsoup4 requests icalendar \--save

\# (Optional) Verify all packages are registered and in sync

uv pip list

---

# 4\. Database Schema Migration Script (Alembic / PostgreSQL)

To apply the schema extensions defined in the Technical Specification, run the following SQL commands. This initializes the `pgvector` index (Phase 1), Stripe/License tracking tables (Phase 2), and iCal reservation/messaging tables (Phase 3):

\# Access the local SQLite database via command line

sqlite3 hosteva.db \<\<SQL\_MIGRATION

\-- \--- PHASE 1: pgvector & Semantic Search (Production PostgreSQL) \---

\-- CREATE EXTENSION IF NOT EXISTS vector;

\-- ALTER TABLE ordinances ADD COLUMN embedding vector(1536);

\-- \--- PHASE 2: Stripe Billing & License Registry \---

CREATE TABLE IF NOT EXISTS subscriptions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    host\_id INTEGER NOT NULL,

    stripe\_customer\_id TEXT UNIQUE,

    stripe\_subscription\_id TEXT UNIQUE,

    tier TEXT DEFAULT 'FREE',

    status TEXT DEFAULT 'INACTIVE',

    created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS permit\_transactions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    property\_id INTEGER NOT NULL,

    stripe\_session\_id TEXT UNIQUE,

    payment\_status TEXT DEFAULT 'PENDING',

    amount\_paid REAL DEFAULT 150.0,

    created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,

    FOREIGN KEY(property\_id) REFERENCES properties(id) ON DELETE CASCADE

);

\-- \--- PHASE 3: Simplified iCal Sync & Unified Inbox \---

CREATE TABLE IF NOT EXISTS reservations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    property\_id INTEGER NOT NULL,

    ota\_source TEXT NOT NULL,

    external\_booking\_id TEXT NOT NULL UNIQUE,

    guest\_name TEXT NOT NULL,

    check\_in DATE NOT NULL,

    check\_out DATE NOT NULL,

    gross\_revenue REAL DEFAULT 0.0,

    tax\_liability REAL DEFAULT 0.0,

    payout\_status TEXT DEFAULT 'PENDING',

    created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,

    FOREIGN KEY(property\_id) REFERENCES properties(id) ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS guest\_messages (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    property\_id INTEGER NOT NULL,

    ota\_source TEXT NOT NULL,

    sender\_name TEXT NOT NULL,

    message\_text TEXT NOT NULL,

    ai\_suggested\_reply TEXT,

    is\_replied INTEGER DEFAULT 0,

    created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,

    FOREIGN KEY(property\_id) REFERENCES properties(id) ON DELETE CASCADE

);

SQL\_MIGRATION

---

# 5\. Application & Worker Verification Run

Verify that the FastAPI web server and Celery background workers boot concurrently without errors after database schema upgrades:

\# 1\. Start the Celery Worker Process

celery \-A app.tasks worker \--loglevel=info \--beat

\# 2\. Start the FastAPI Application Server

uvicorn app.main:app \--host 127.0.0.1 \--port 8000 \--reload  
