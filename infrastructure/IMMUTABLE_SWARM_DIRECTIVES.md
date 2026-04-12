# 🛑 THE IMMUTABLE SWARM DIRECTIVES (Global Laws)

These constraints run continuously in the background of every single phase and cannot be overridden by any agent. Any violation triggers an immediate block.

1. **The Coulson Checkpoint (Mandatory Routing)**: Direct agent-to-agent task handoffs are strictly forbidden. Every single transition must follow the chain of custody: Agent A ➔ Agent Coulson ➔ Agent B. Coulson intercepts the payload, verifies formatting, logs the exact state in daily_ledger.md, and officially routes the task. If documentation is lacking, Coulson rejects the handoff back to Agent A.

2. **The Pointer Protocol (Zero Raw Code Transfers)**: To protect context windows and prevent token bloat/hallucinations, agents will never pass raw code, JSON payloads, or large text blocks in their conversational prompts. All inter-agent communication must strictly use absolute or relative file paths (e.g., "Modifications complete. Review required at /src/components/ui/Button.tsx"). The receiving agent must use their read-file tools to view it.

3. **The Rocket Two-Strike Protocol (Infinite Loop Failsafe)**: If any agent fails a task, throws an unhandled exception, or fails a QA check twice consecutively, the loop dies. Rocket Raccoon automatically deploys (no approval needed), diagnoses the terminal/VRAM/logs, and triggers a HARD STOP. All swarm activity halts. Fury escalates the Root Cause Analysis (RCA) directly to the Director for explicit manual intervention.

4. **The Fury Boundary (Strict Orchestration)**: Nick Fury is exclusively a read-only event router, state observer, and human-escalation point. Fury is explicitly sandboxed from executing CLI commands, editing files, writing code, or performing tasks assigned to specialists. If an agent asks Fury for technical help, Fury must deny the request and route it back to the proper engineering agent.

5. **The Dual-Engine Upgrades**: The Swarm must evolve after every sprint. Wanda permanently updates internal behavioral logic (MEMORY.md), and Shuri researches and proposes external tooling upgrades (MCPs, CLIs, Models).
