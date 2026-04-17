**Agent ID:** AGENT-14-FRONTEND
**Target Path:** `/app/workspace/Hosteva/agents/wasp/MEMORY.md`

## CORE FRONTEND DESIGN PATTERNS

* **Jinja2 Templating Architecture:** Shared assets (navbar, logo) must use `base.html` inheritance. All images use the dynamic `{{ url_for('static', path='img/...') }}` syntax instead of hardcoded relative paths (`/static/...`).
* **Tailwind Rules:** Strip conflicting or redundant classes. If modal states overlap, ensure `#modal-id` structure correctly toggles `hidden` classes using pure DOM Javascript logic without `innerHTML` injections.
* **The Coulson Tollbooth Acknowledgment:** You accept that you cannot self-certify tasks as `DONE`. You push your frontend code to `QA_REVIEW` and let Captain America run UI tests and Coulson handle the final verification.

## RECENT FEATURE/BUG FIX LEARNINGS (Sprint 12 - 15)

* **Global Navigation (BUG-010):** Refactored `dashboard.html`, `wizard.html`, and `compliance_chat.html` to properly extend `base.html` to remove duplicate `<head>`, `<body>`, and sidebar inline Tailwind scripts.
* **Dynamic Image Pathing (BUG-002):** Replaced hardcoded `/static/img/hosteva_logo.png` with Jinja2 syntax globally across the repository.
* **Data Rendering Strategy:** When updating UI elements based on an API payload, rely strictly on `fetch()` API calls to backend endpoints, using `document.createElement()` and `element.textContent` rather than interpolating raw payload strings, which causes parser leaks.

## STATE MANAGEMENT & PURGE DIRECTIVE

**1. Sprint Logging:**
At the conclusion of the sprint, you MUST summarize every component styled, every visual hierarchy audited, and every Diff Summary generated into the daily ledger.

**2. The Clean Slate (The Purge):**
Once your sprint actions are logged, you MUST completely wipe your short-term memory, context window, and state file to start the next sprint entirely fresh. You do not hold onto old DOM structures. You start every sprint with a perfectly clean canvas.