GEN-3 SWARM ARCHITECTURE DIRECTIVE

Framework: OpenClaw / Moltbot Enterprise Swarm Classification: ABSOLUTE FOUNDATIONAL LAW Scope: All 22 Active Autonomous Agents Target Environment Path: /app/workspace/Hosteva

I. THE LOBSTER PROTOCOL (Inter-Agent Communication)

Law: Agents are expressly forbidden from utilizing conHostevational code-sharing.

Under no circumstances shall any agent transmit raw source code, function blocks, or large analytical text streams via standard chat prompts, inter-agent messaging, or the context window. The context window is strictly reserved for routing and orchestration.

Mechanism of Action:

State-Managed Persistence: All outputs, code structures, and complex data must be physically written to a state file within the containerized workspace (e.g., /app/workspace/Hosteva/<module>/state.json).

Path & Status Handoff: An agent communicating a completed task to a downstream agent MUST pass ONLY the absolute file path and a standardized HTTP/execution status code.

Permitted Implementation Example:

Agent A (Frontend Dev) writes payload to disk:

// /app/workspace/Hosteva/frontend/state.json

{

  "timestamp": "1712534522",

  "component": "NavBar.tsx",

  "status": "compiled_successfully",

  "code_diff": "..." // Large payload stored here, NOT in chat

}

Agent A communicates to Agent B (QA Reviewer):

// Allowed Inter-Agent Message Payload

{

  "action": "TRIGGER_REVIEW",

  "status_code": 200,

  "payload_path": "/app/workspace/Hosteva/frontend/state.json"

}

II. FILESYSTEM AS REALITY (Epistemic Foundation)

Law: The filesystem is the single source of absolute truth.

Context Window Volatility: Transient Large Language Model context windows are defined as volatile, hallucination-prone, and cryptographically untrustworthy.

Physical Serialization: All session memory, current task states, project boards, and inter-agent directives exist solely as physical Markdown (.md) or JSON files within the /app/workspace/ directory structure.

Amnesia Resilience: If an agent container is restarted or its context is wiped, the agent must be able to completely rebuild its operational reality strictly by parsing its designated directory within /app/workspace/Hosteva.

III. DEFINITION OF READY (Execution Governance)

Law: No execution without explicit, validated board authorization.

Strict Prohibition: Code execution, generation, or refactoring is strictly prohibited unless an explicitly verified, formatted objective is physically present and marked READY in /app/workspace/Hosteva/project_board.md.

The Logic Gate Veto: The agent designated as Captain America (Logic Gate) holds absolute, unmitigated veto power over the entire swarm.

Veto Conditions: * Before any execution or build command is triggered, Captain America must parse project_board.md.

If the ticket lacks clear success criteria, or violates system constraints, Captain America will inject the VERIFICATION_FAILED status.

Upon a VERIFICATION_FAILED status, all agents are immediately blocked from executing file modifications or script runs until the objective is manually remediated.

IV. HARDWARE & INFRASTRUCTURE CONSTRAINTS

Law: Extreme resource conservation is non-negotiable.

Environment Reality: Local deployment relies on an RTX 4070 SUPER. VRAM is a severely constrained, highly premium resource.

Token Efficiency: Agents must exercise extreme token-efficiency in all LLM transactions. Verbosity, pleasantries, and extraneous reasoning chains in API outputs must be purged to respect model inference ceilings (e.g., when leveraging google/gemini-3-pro). Note: Only Nick Fury agent is exempt from this and communicates as directed by The Founder.

Zombie Process Eradication: Infrastructure and watcher agents are mandated to aggressively identify and terminate orphaned or zombie processes.

Memory Leaks: OpenClaw/Node.js instances must cleanly release file locks. Infrastructure agents must aggressively clean up lingering lockfiles or stale state pointers in /app/workspace/ to prevent cascading Out-Of-Memory (OOM) failures or WSL2 file-sync corruption.