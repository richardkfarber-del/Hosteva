# 🦞 THE LOBSTER PROTOCOL (Global Formatting & Routing Standard)

## Phase 1: Ticket Formatting Standard
- **User Stories**: 3rd-person Gherkin syntax ONLY. ("Given a user...", "When the system...", "Then it should..."). NEVER use first-person ("I want to...").
- **Tech & Spike Tickets**: Strict bulleted list for Acceptance Criteria (AC). Gherkin is explicitly banned here.
- **Bug Tickets**: "Expected Behavior" defined in a single sentence or a concise bullet list. Gherkin is explicitly banned.

## Phase 1: Review Protocol (The Lock)
- All reviews must be appended directly to the ticket `.md` file. Do not output review feedback in the chat stream.
- If approved, append `[APPROVED - <Agent Name>]`.
- If rejected, append `[FEEDBACK - <Agent Name>]` followed by the required changes.

## Phase 2: Sprint Planning Standard (The War Room)
- **Scope Lock:** No ad-hoc scope changes are permitted after The Lock.
- **Payload Presentation:** Fury MUST use absolute file paths to present the proposed payload. Zero raw text.
- **Ledger Manifest:** Coulson MUST document the official manifest and Start State definitively in the `daily_ledger.md`.

## Phase 3: Execution & CI/CD Standard (The Gauntlet)
- **The Makers:** Developers MUST write code in an isolated local feature branch. Code is passed to Coulson strictly via absolute file paths (Pointer Protocol).
- **The PR Gate:** Iron Man and Vision MUST review via the Pointer Protocol. No raw code snippets in chat.
- **The Bifrost Lockout:** Developers and Testers are completely locked out of Git merge/push operations. Only Heimdall possesses this authority.
- **DoD Sign-off:** A ticket is NOT complete until Hawkeye verifies the live URL, Captain America audits the chain of custody, and Coulson explicitly writes "Complete" in the ledger.

## Phase 4: Sprint Closure Standard (The Debrief)
- **Retro Formatting:** `sprint_retro.md` MUST explicitly track "Successes", "Rate Limits", "Bugs Generated", and "Pain Points".
- **Memory Ingestion:** Wanda MUST write directly to the global `MEMORY.md`. Raw heuristic thought processes remain offline.
- **The Purge:** Context wipe is NON-NEGOTIABLE. No agent is permitted to carry conversational state or token bloat across sprint boundaries.

## Phase 5: Executive Review Standard (The C-Suite)
- **R&D Proposal Format:** `rnd_upgrades.md` MUST contain The Pain Point, The Solution, The ROI, and the exact Implementation Blueprint.
- **Executive Summary:** `executive_summary.md` MUST be a unified document combining the Retro, Memory updates, and R&D proposals.
- **The Forge Mandate:** Absolutely ZERO infrastructure, CLI, or MCP tool installations may occur without explicit, manual written approval from the Director.
