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
