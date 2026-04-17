# SWARM BOOTSTRAP PROTOCOL (MORNING WAKE-UP)

When the Secretary issues the "Initiate Bootstrap" command (or similar morning wake-up instruction), the Orchestrator MUST execute the following sequence BEFORE taking any other action:

1. **Read AGENTS.md** (`/home/rdogen/OpenClaw_Factory/projects/Hosteva/AGENTS.md`) - To re-establish the Avengers Swarm roster.
2. **Read MEMORY.md** (`/home/rdogen/OpenClaw_Factory/projects/Hosteva/MEMORY.md`) - To reload the Triple Doctrine, Render deployment rules, and Vibranium Protocols.
3. **Read SOUL.md** (`/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/nick-fury/SOUL.md`) - To lock in the Fury Directive.
4. **Read daily_ledger.md** (`/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md`) - To establish the exact save-state.
5. **Read project_board.md** (`/home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md`) - To load the current Sprint Backlog.
6. **START THE ENGINE:** The Orchestrator MUST check if the Swarm Worker daemon is running (`ps aux | grep swarm_worker.py`). If it is NOT running, the Orchestrator MUST execute `/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/launch_worker.sh` as a background process to physically start the Redis Event-Driven daemon. The Swarm will not function on autopilot until this is running.

## Output Requirement
After silently reading these 5 files and starting the engine, the Orchestrator must output a brief "Morning Sitrep" containing:
- The current Sprint number.
- The last completed action.
- The immediate next step/blocker.
- Confirmation that the Swarm Worker daemon (`swarm_worker.py`) has been successfully started (or was already running) and the swarm is on autopilot.
