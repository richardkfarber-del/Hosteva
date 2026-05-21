# V3 GraphBit Implementation Plan

## The Current State
1. `workflow.py` contains the old, monolithic V2 GraphBit pipeline (28 nodes connected in a massive chain).
2. `scrum_master.py` is our new V3 Orchestrator. It correctly manages the state (`swarm_state.json`) and the kickback loop.
3. The 13 scripts in `scrum_pipelines/` (e.g., `04_tdd.py`, `05_execution.py`) are currently **dummy stubs**. They print the correct agent and skill names but do not actually import or execute GraphBit.

## The Objective
We need to shatter the monolithic `workflow.py` and distribute its GraphBit logic into the 13 individual `scrum_pipelines/` scripts. Each phase will become its own isolated, deterministic GraphBit mini-workflow.

## Required Updates (File by File)

### 1. Shared Infrastructure (New File: `scrum_pipelines/gb_config.py`)
We need a centralized configuration file to prevent repeating GraphBit setup in all 13 scripts.
*   Initialize GraphBit (`init()`).
*   Define LLM Configs (`LlmConfig.ollama('llama3.1-orchestrator')`, `coder_config`, etc.).
*   Define MCP Tool wrappers (e.g., `docker_mcp_provision()`, `chromadb_query()`) so they can be passed to the agents.

### 2. Phase 1-4: Planning & Setup
*   **`01_intake.py`**: 
    *   Create GraphBit Workflow.
    *   Add Node: Hawkeye (Business Analysis Skill + ChromaDB tool).
    *   Add Node: Falcon (Market Recon Skill + Web Search tool).
*   **`02_planning.py`**:
    *   Add Node: Vision & Kang (Architecture Skill, Gemini override).
    *   Add Node: She-Hulk (Compliance Audit Skill).
*   **`03_backlog.py`**:
    *   Add Node: Hawkeye & Coulson (Backlog Grooming Skill + File Write tools).
*   **`04_tdd.py`**:
    *   Add Node: Black Widow (QA Generation Skill + Docker MCP tool).

### 3. Phase 5-7: The Core Loop
*   **`05_execution.py`**:
    *   Add Nodes: Iron Man, Wasp, Hulk, Shang-Chi (Core Implementation Skill).
    *   *Logic*: Inject `kickback_context` from `swarm_state.json` into the prompt if it exists.
*   **`06_review.py`**:
    *   Add Node: Captain America (PR Review Skill).
    *   *Logic*: Parse output. If `### 🔴 [BLOCKING]`, trigger `sys.exit(1)`.
*   **`07_security.py`**:
    *   Add Node: Black Panther & Ultron (Security Audit Skill).
    *   Add Node: She-Hulk (Legal Compliance Skill).
    *   *Logic*: Trigger `sys.exit(1)` on breaches.

### 4. Phase 8-13: Deployment & Wrap-up
*   **`08_deploy.py`**: Heimdall & Rocket (Deployment Skill + Docker/Render tools).
*   **`09_uat.py`**: Spider-Man & Wasp (UI/UX Skill).
*   **`10_retro.py`**: Jarvis & Thanos (Telemetry Skill).
*   **`11_memory.py`**: Wanda & Winter Soldier (Memory Skill).
*   **`12_executive.py`**: Nick Fury (Team Comm Skill).
*   **`13_consolidation.py`**: Star-Lord (Marketing Skill).

## Execution Strategy
1. Create `gb_config.py` to establish the GraphBit baseline and tools.
2. Rewrite the scripts one by one, starting with `04_tdd.py` (since that is where we paused for the Stripe bug).
3. Test the execution of each script locally before moving to the next.

This completely replaces the `# TODO` stubs with actual, executable LLM nodes.