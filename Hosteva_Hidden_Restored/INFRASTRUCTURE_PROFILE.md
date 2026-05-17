# Hosteva Infrastructure Profile

This document outlines the highly customized environmental constraints for the Hosteva project. ALL agents (especially Rocket Raccoon and Nick Fury) MUST adhere to these rules for all diagnostic and deployment commands.

## 1. The Operating Environment (WSL2 & Pathing)
* **Host:** Running Ubuntu on WSL2 inside a Windows machine.
* **Project Isolation:** Do NOT use a global system-level OpenClaw installation. The environment is completely isolated in `/home/rdogen/OpenClaw_Factory/projects/Hosteva`.

## 2. The Gateway & Daemon Rules
* **NO SYSTEMCTL:** Because the environment is isolated, Linux system services are NOT used. NEVER suggest running `openclaw gateway restart`, `openclaw gateway start`, or any `systemctl` commands.
* **Launch Protocol:** The Helicarrier is booted exclusively via the custom `./launch.sh` script running in the foreground. To restart the gateway, the ONLY acceptable protocol is to kill the active process (`killall -9 openclaw-gateway` or `Ctrl+C` the terminal) and run `./launch.sh`.

## 3. The Local Compute Bridge (Ollama)
* **Separation of Compute:** OpenClaw runs in WSL (Linux), but Ollama runs natively on the Windows Host.
* **Network Routing:** Do not assume Ollama is on `localhost:11434`. The WSL bridge requires the true Windows IP. This routing is managed exclusively via the `.env` file (`OLLAMA_BASE_URL`). If the bridge fails, do not suggest `openclaw configure`—alert the Director that the WSL IP route needs updating.

## 4. Package Management (PEP 668)
* **Strict Python Rules:** The Ubuntu environment strictly enforces PEP 668. NEVER suggest installing global CLI tools using `python -m pip` or `pip install`.
* **The Pipx Mandate:** Any global Python tool (like Aider) MUST be installed using `pipx` (e.g., `pipx install aider-chat`).

## 5. Configuration Integrity
* **No Manual JSON Edits:** Never suggest opening `openclaw.json` in a text editor like Notepad. It corrupts the CRLF encoding. All configuration changes must be handled via the CLI (`openclaw config set...`) or native Node.js injection scripts.

## 6. The "Infinite Reload" Failsafe (Daemon Ban)
* **NO INFINITE BACKGROUND POLLING:** The OpenClaw gateway actively monitors the workspace directory. Any Python daemon running an infinite `while True` loop that touches or polls the filesystem will trigger a continuous `[reload]` cascade, effectively assassinating all active agents and crashing the Helicarrier.
* **Single-Execution Only:** The "Sprint Flush" (or any automation) MUST NEVER be implemented as a continuous background daemon. It must be a standard, single-execution script that runs ONLY when explicitly triggered, performs its job, and immediately exits.

### Systemic Failsafe: Web Tool Timeouts & Transparency
- **Hard Timeouts:** All `web_search`, `web_fetch`, and `browser` tool executions MUST enforce a strict wall-clock timeout. If a process does not resolve within 30 seconds, the tool wrapper must sever the connection and return a hard error to prevent main-thread starvation.
- **Asynchronous Heartbeats:** To prevent silent failures, heartbeat intervals must run in an isolated execution context. If an agent's main loop hangs and misses a check-in, the isolated heartbeat must automatically terminate the stalled process.
- **Mandatory Notification (The Transparency Rule):** If an agent is unsuccessful in utilizing an expected external tool (e.g., Bruce Banner experiencing a CAPTCHA trap during an R&D web scrape), the agent is explicitly FORBIDDEN from silently falling back to internal knowledge without notifying the Director. Any tool failure or forced degradation (e.g., `browser` -> `web_fetch`) MUST trigger an immediate, high-priority alert to the Orchestrator, who will then present the failure to the Director. Silent fallbacks are a violation of swarm transparency.
