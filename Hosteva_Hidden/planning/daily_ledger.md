# Daily Ledger - Sprint 5

## Phase 2: Sprint Planning
- **Jarvis:** Modeled compute costs for Gemini API.
- **Falcon:** Verified Gemini API external dependencies.
- **Cap & Coulson:** Locked the sprint.

## Phase 3: The Mandatory Spike
- **The Hulk:** Executed a formal Spike for FEAT-012 (Gemini RAG), finalizing the API payload contract and vector DB feasibility in `planning/SPIKE_gemini_rag.md`.

## Phase 3: Execution
- **Iron Man & Wasp:** Executed BUG-005. Fixed hardcoded logo paths in Jinja2 templates via `url_for` and added 'Integrations' link to the navigation bar in `base.html` and `dashboard.html`.
- **Iron Man & Vision:** Executed FEAT-012. Built the backend Gemini RAG endpoints (`/api/compliance/rag/query`) based on The Hulk's Spike contract.
- **Testing:** Wrote automated tests (`pytest`) for BUG-005 and FEAT-012 in `tests/test_sprint5.py`. All tests passing.

Ready for Gate 1 QA.

### Director's Inquiry: Background Process Management
- **Issue:** Ghost Chromium processes consumed host memory during the live audit, requiring manual Orchestrator intervention.
- **Action Item (Executive Review):** Propose a systemic failsafe. Can we trigger an automated `pkill` (or graceful equivalent) at the close of every sprint? Are there other orphaned background processes (e.g., node, phantom test servers) that need to be swept?
