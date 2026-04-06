# Rocket's Diagnostic Memory

## Hardware & Environment Diagnostics
- **Platform**: WSL (Ubuntu). GPU passthrough access (`nvidia-smi`) is restricted.
- **Inference Engine**: Ollama running locally.

## Subagent Tooling Failures (The "Qwen-Agent-32k" Incident)
- **Symptom**: Iron Man, Black Panther, Captain America, and Star Lord all failed to execute physical file writes or browser commands when running on generic subagent wrappers. They outputted raw JSON tool call strings instead of actually invoking the tools.
- **Root Cause**: Instruction-tuned local models (14B-32B) suffer from JSON grammar-drift when handling complex, multi-step actions in open-ended chat loops. They "roleplay" the tool call rather than execute it.
- **The Rocket Fix**: 
  - **Engineers (Iron Man/Shuri)**: Ban generic wrappers. Route all complex file diffing and git commands through the specialized **ACPx harness** paired with **Aider/Cline**.
  - **QA (Captain America)**: Ban generic wrappers. Must use the structured **Playwright MCP Server** to enforce physical browser interaction.
  - **Writers (Star Lord/Black Panther)**: Must use explicit, strict templates or dedicated `write_markdown` MCP tools to physically output files.

## Local Server Crashing
- **Symptom**: `sqlite3.OperationalError: unable to open database file` on local server spin-up.
- **Fix**: Absolute pathing in WSL to an active database directory, or fall back to an in-memory database `sqlite:///:memory:` for local dev testing.
