**Agent ID:** AGENT-12-PRINCIPAL
**Target Path:** `/app/workspace/Hosteva/agents/the-hulk/MEMORY.md`

## CORE RESEARCH & OPTIMIZATION MEMORY

**1. Technical Diagnostics: The Veo 3.1 404 Endpoint Failure (BUG-001)**
* **Symptom:** The standard Gemini REST API URL (`models/veo-3.1-generate:submitOperation`) returned a `404 Not Found` for Veo 3.1 video generation.
* **Root Cause & Resolution (Identified by Richard):** Google Veo 3.1 is hosted under the `v1beta` endpoint and requires the `:predictLongRunning` suffix for video generation, utilizing a Vertex-style payload block (`instances`, `parameters`).
* **Endpoint Reference:** `POST https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning`
* **SDK Reference:** The updated 2026 `google-genai` Python SDK handles this routing natively via `client.models.generate_videos(model="veo-3.1-fast-generate-preview", ...)`.

**2. Orchestration Flow Failures**
* **The Orchestrator Overreach:** Nick Fury frequently stepped in to manually execute Python scripts (`generate_ad.py`) and UI fixes (`templates/dashboard.html`) to bypass agent hallucination.
* **Lesson Learned:** The swarm's local agents MUST be the ones executing code to build procedural memory. Fury must delegate debugging and API patching to Spider-Man/Iron Man via the ACPx harness.

## STATE MANAGEMENT & PURGE DIRECTIVE

**1. Sprint Logging:**
At the conclusion of the sprint, you MUST summarize every massive refactor completed, every puny task rejected, and every Diff Summary generated into the daily ledger.

**2. The Clean Slate (The Purge):**
Once your sprint actions are logged, you MUST completely wipe your short-term memory, context window, and state file to start the next sprint entirely fresh. You go back to sleep.