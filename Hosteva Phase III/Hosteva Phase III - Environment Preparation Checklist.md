# Hosteva — Environment Preparation Checklist (Phase III: Multi-State GTM & AI Agentic Launch)

This document details the exact terminal initialization, database migration commands, and dependency installations that the Google Antigravity agent must execute before writing any application code for Phase III.

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
- **PDF Form Template Directory:** `/working_dir/app/static/form_templates/`

---

# 3\. Dependency Scaffolding Commands

Execute the following commands from the root repository directory to install the new packages required for PDF form-filling, web scraping, and vector search operations:

\# Activate the python virtual environment

source .venv/bin/activate

\# Install PDF, scraping, and web crawling packages

uv pip install pypdf reportlab beautifulsoup4 requests httpx \--save

\# (Optional) Verify all packages are registered and in sync

uv pip list

---

# 4\. Database Schema Migration Script (Alembic / PostgreSQL)

To apply the schema extensions defined in the Technical Specification, run the following SQL commands. This initializes the `is_ai_scraped` and `is_expert_verified` tracking fields in the `municipal_codes` table, and maps the `state` properties in `properties` and `municipal_codes`:

\# Access the local SQLite database via command line

sqlite3 hosteva.db \<\<SQL\_MIGRATION

\-- \--- PHASE III: MULTI-STATE GTM & AI AGENTIC SCALINGS \---

\-- 1\. Extend the municipal\_codes table to handle scraping and PDF templates

ALTER TABLE municipal\_codes ADD COLUMN state TEXT DEFAULT 'FL';

ALTER TABLE municipal\_codes ADD COLUMN is\_ai\_scraped INTEGER DEFAULT 0;

ALTER TABLE municipal\_codes ADD COLUMN is\_expert\_verified INTEGER DEFAULT 0;

ALTER TABLE municipal\_codes ADD COLUMN scraped\_at TIMESTAMP;

ALTER TABLE municipal\_codes ADD COLUMN form\_template\_path TEXT;

\-- 2\. Extend the properties table to handle multi-state parameters

ALTER TABLE properties ADD COLUMN city TEXT;

ALTER TABLE properties ADD COLUMN county TEXT;

ALTER TABLE properties ADD COLUMN state TEXT DEFAULT 'FL';

ALTER TABLE properties ADD COLUMN zip\_code TEXT;

SQL\_MIGRATION

---

# 5\. Application & Worker Verification Run

Verify that the FastAPI web server and Celery background workers boot concurrently without errors after database schema upgrades:

\# 1\. Start the Celery Worker Process

celery \-A app.tasks worker \--loglevel=info \--beat

\# 2\. Start the FastAPI Application Server

uvicorn app.main:app \--host 127.0.0.1 \--port 8000 \--reload  
