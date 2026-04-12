# Phase 4: Full-Spectrum Live UAT Regression Checklist

**Target Environment:** `https://hosteva.onrender.com`

## Execution Protocol
Black Widow must execute each of these tasks sequentially as isolated micro-tasks to prevent context collapse. As new features are built, their validation steps MUST be added to this checklist.

### 1. Core Routing & Endpoints
- [x] **Micro-Task 1:** Health check root endpoint (`/`). Expect `200 OK`.
- [x] **Micro-Task 2:** Health check Address Eligibility (`/wizard`). Expect `200 OK` (Validates BUG-001).
- [x] **Micro-Task 3:** Health check Host Dashboard (`/dashboard`). Expect `200 OK` (Validates FEAT-002, FEAT-011).

### 2. Live Database Integration
- [x] **Micro-Task 4:** Execute Florida Ordinance seed script against the live PostgreSQL database (`python3 app/scripts/seed_florida_ordinances.py`). Expect successful data injection.

### 3. UI/Visual Regression (DESIGN_STATE.md)
- [x] **Micro-Task 5:** Verify Glassmorphism and No-Line design tokens render correctly on the `/wizard` UI.
- [x] **Micro-Task 6:** Verify the unified sidebar and data tables render correctly on the `/dashboard` UI.
