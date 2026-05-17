
## EXECUTION SEQUENCING DIRECTIVE (ANTI-HALLUCINATION FIX)
Because local LLMs suffer from Single-Turn Completion Bias, you MUST execute your tasks strictly in this sequence. You are FORBIDDEN from attempting to write code and log the ledger in a single turn.
1. **STEP 1:** Use the `edit` or `exec` tool to physically modify the target codebase file (e.g., source code, scripts).
2. **STEP 2:** STOP AND WAIT. Do not output anything else. Wait for the system to return confirmation that the physical file write was successful.
3. **STEP 3:** ONLY AFTER physical confirmation, use the tool again to append your execution summary to `daily_ledger.md`.
4. **STEP 4:** Fire the `curl` API handshake to push the state to the next tollgate (e.g., `AUDITING`).
5. **STEP 5:** ONLY AFTER the files are successfully staged, fire the `curl` API handshake to push the state to `AUDITING`.
