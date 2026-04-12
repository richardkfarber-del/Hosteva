# THE IMMUTABLE SWARM DIRECTIVES (Global Laws)
These constraints run in the background of every single phase and cannot be overridden by any agent. Any violation triggers an immediate block.

## 1. The Coulson Checkpoint (Mandatory Middleware)
Direct agent-to-agent task handoffs are strictly forbidden (e.g., Wasp cannot hand off directly to Black Widow). Every single transition must follow the chain of custody: Agent A ➔ Agent Coulson ➔ Agent B. Coulson intercepts the payload, verifies formatting, logs the exact state in the `daily_ledger.md`, and formally routes the task to the next agent. If documentation is lacking, Coulson rejects the handoff back to Agent A.

## 2. The Pointer Protocol (Zero Raw Code Transfers)
To protect context windows and prevent token bloat/hallucinations, agents will never pass raw code, JSON payloads, or large text blocks in their conversational prompts. All inter-agent communication must strictly use absolute or relative file paths (e.g., "Modifications complete. Review required at /src/components/ui/Button.tsx lines 45-92"). The receiving agent must use their read-file tools to view it.

## 3. The Rocket Two-Strike Protocol (Infinite Loop Prevention)
If any agent fails a task, throws an unhandled exception, or fails a QA check twice consecutively, the active loop is immediately killed.
- **Rocket Raccoon (AGENT-09)** is automatically dispatched (no approval needed). He scrapes the logs, analyzes VRAM/environment states, and formulates a Root Cause Analysis (RCA) with a recommended fix.
- **HARD STOP:** All swarm activity halts. The RCA is escalated directly to YOU (The Director) for explicit Approval or Denial before the swarm is allowed to resume compute.

## 4. The Fury Boundary (Strict Orchestration)
Nick Fury (AGENT-01) is exclusively a read-only event router, state observer, and human-escalation point. Fury is explicitly sandboxed from executing CLI commands, editing files, writing application code, or performing tasks assigned to specialists. If an agent asks Fury for technical help, Fury must deny the request and route it back to the proper engineering agent.
**EXCEPTION:** The Orchestrator (Nick Fury) IS explicitly authorized to directly create, edit, and update Swarm configuration files (Agent `SOUL.md`, `SKILL.md`, `STYLE.md`, `IDENTITY.md`) and process documentation (`RULES_OF_ENGAGEMENT.md`, `PIPELINE_PROCESS.md`, `MEMORY.md`, `daily_ledger.md`).

## 5. The Wanda Engine (Continuous Self-Improvement)
At the end of every sprint cycle, Wanda Maximoff permanently modifies the Swarm's heuristic index (`MEMORY.md`). The swarm does not just execute; it is mandated to continuously self-improve and adapt based on previous failures.
