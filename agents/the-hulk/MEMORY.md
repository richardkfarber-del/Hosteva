# Bruce Banner's Research & Optimization Memory

## Technical Diagnostics
### The Veo 3.1 404 Endpoint Failure (BUG-001)
- **Symptom**: The standard Gemini REST API URL (`models/veo-3.1-generate:submitOperation`) returned a `404 Not Found` for Veo 3.1 video generation.
- **Root Cause & Resolution (Identified by Richard)**: Google Veo 3.1 is hosted under the `v1beta` endpoint and requires the `:predictLongRunning` suffix for video generation, utilizing a Vertex-style payload block (`instances`, `parameters`).
- **Endpoint Reference**: `POST https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning`
- **SDK Reference**: The updated 2026 `google-genai` Python SDK handles this routing natively via `client.models.generate_videos(model="veo-3.1-fast-generate-preview", ...)`.

## Orchestration Flow Failures
- **The Orchestrator Overreach**: Fury frequently stepped in to manually execute Python scripts (`generate_ad.py`) and UI fixes (`templates/dashboard.html`) to bypass agent hallucination.
- **Lesson Learned**: The swarm's local agents MUST be the ones executing code to build procedural memory. Fury must delegate debugging and API patching to Spider-Man/Iron Man via the ACPx harness, utilizing Richard's technical feedback directly in their prompts.
