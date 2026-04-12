# Sprint 1 Backlog: Regression Remediation

## Bugs

### BUG-01: Global CSS & Tailwind Class Corruptions
- **Description:** Botched find-and-replace corrupted Tailwind border utility classes across Home, Wizard, and Dashboard (e.g., `-none` instead of `outline-none`, `border-none-radius`, `border-none -white/10`).
- **Expected Behavior:** 
  - All corrupted CSS and Tailwind classes are restored to their standard equivalents (e.g., `border-b-2`, `border-white/80`, `border-radius`).
  - Layouts, borders, focus states, and rounded corners render correctly without visual artifacts.

### BUG-02: Wizard Address Check API Routing Mismatch
- **Description:** The `/wizard` UI calls a mock endpoint (`/wizard/audit`) rather than the production Geocoding API, resulting in dummy "Pass/Fail" data instead of true traffic light status.
- **Expected Behavior:** The wizard UI fetches from `/api/eligibility/check` and correctly maps the production payload (`jurisdiction`, `status`, `conditions`, `components`) into the frontend display.

### BUG-03: Modal Focus Trapping on Dashboard
- **Description:** Dashboard Modals (Add Property, Filters) do not trap focus, allowing background interactions.
- **Expected Behavior:** When any dashboard modal is active, keyboard and pointer focus are strictly trapped within the modal overlay.

### BUG-04: Autocomplete Dropdown Accessibility
- **Description:** The autocomplete dropdown across Home, Wizard, and Dashboard lacks keyboard navigation support.
- **Expected Behavior:** Users can fully navigate the autocomplete dropdown using the Up/Down arrow keys and select a suggestion using the Enter key.

### BUG-05: Dead Navigation Links
- **Description:** Multiple navigation links on the Home page, Dashboard sidebar, and Wizard point to orphaned `#` href attributes.
- **Expected Behavior:** All orphaned `#` links are replaced with actual routing paths or visually disabled to indicate they are inactive.

### BUG-06: Harsh Dashboard Pulse Animations
- **Description:** Active alert counters and violation badges use an unthrottled `animate-pulse` utility, causing visual fatigue.
- **Expected Behavior:** The `animate-pulse` utility is either removed, visually softened, or wrapped in a modifier that respects the user's `prefers-reduced-motion` OS setting.

## Tech/Spikes

### TECH-01: Deprecate Mock Wizard Audit Endpoint
- **Description:** The dummy `/wizard/audit` endpoint in `main.py` is obsolete and risks future routing regressions.
- **Acceptance Criteria:**
  - The `@app.post("/wizard/audit")` endpoint and associated mock logic are completely deleted from `main.py`.
  - All frontend references to `/wizard/audit` are removed from the codebase.

## User Stories

### STORY-01: Unified Application Navigation Shell
- **Description:** The user experience is disjointed due to disparate navigation layouts (top bar on Home, light sidebar on Wizard, dark sidebar on Dashboard) and inconsistent hardcoded user states.
- **Acceptance Criteria:**
  - Given a user navigates between the Wizard and Dashboard modules
  - When the pages are rendered by the application
  - Then the application displays a single, cohesive layout shell and sidebar component
  - And the application renders a consistent authenticated user profile state across all views

[APPROVED - Vision]

[APPROVED - Iron Man]

[FEEDBACK - Captain America]
The backlog has clear scope and testability (Gherkin/Expected Behaviors), but it lacks a formal Definition of Done (DoD) for the Sprint. Furthermore, I am awaiting Iron Man's review before we can SEAL the ticket.

[APPROVED - Iron Man]
Backend architecture and routing rules (specifically `/wizard/audit` deprecation and `/api/eligibility/check` mappings) are fully solid. No flaws detected.
## Definition of Done (DoD)
- All automated unit and integration tests pass successfully (0 critical failures).
- Legacy regression tests confirm no existing features are broken.
- Heimdall reports a stable 200 OK boot from the Render webhooks.
- Hawkeye completes User Acceptance Testing (UAT) and visually verifies the UI fixes.
- Captain America verifies no chain-of-custody breaks occurred during The Gauntlet.
- Coulson formally seals the ledger marking all remediation tickets "Complete".

[SEALED - Captain America]
