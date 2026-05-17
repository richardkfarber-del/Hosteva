# Hosteva Phased Assembly Line Plan (V2 Scrum Pipeline)

## Architecture Overview
The monolithic structure has been completely dismantled. The factory floor now operates as discrete, isolated phases. Each phase runs as a standalone Python script, producing an artifact. If a phase succeeds, the shell loop advances. If a phase fails or triggers a kickback, the loop routes to a Coulson Intervention script.

## Phase Breakdown

*   **Phase 01: Planning** (`run_01_planning.py`) - Intake, ADR, Architecture, Security, UI/UX (Nick Fury, Vision, Falcon, Iron Man, She-Hulk, Black Panther, Wasp).
*   **Phase 02: Ticket Creation** (`run_02_ticket_creation.py`) - Hawkeye converts Phase 1 artifacts into actionable engineering tickets.
*   **Phase 03: Planning Poker / Refinement** (`run_03_planning_poker.py`) - Cross-functional team (Hulk, Shang-Chi, Wasp, Vision, Spider-Man, Ant-Man) reads tickets and assigns Fibonacci complexity scores.
*   **Phase 04: Environment Setup** (`run_04_environment_setup.py`) - DB, Logic, Docs, and VRAM checks (Hulk, Shang-Chi, Spider-Man, Ant-Man, Jarvis, Captain America).
*   **Phase 05: Development** (`run_05_development.py`) - TDD, Backend, Frontend (Black Widow, Iron Man, Wasp).
*   **Phase 06: QA & Deploy** (`run_06_qa_deploy.py`) - PR review, QA environment testing, and deployment (Quicksilver, Spider-Man, Heimdall, War Machine [SRE]).
*   **Phase 07: Shadow Ops & Maintenance** (`run_07_shadow_ops.py`) - Pen-testing, chaos engineering, background updates (Ultron, Thanos, Star-Lord, Wanda, Kang, Shuri).
*   **Phase 08: Retrospective (W.O.R.M. Protocol)** (`run_08_retrospective.py`) - The swarm analyzes the ledger and artifacts to improve the next sprint. Winter Soldier (Tech Debt) and Rocket Raccoon (DevOps/Triage) analyze the system for improvements.
*   **Ad-Hoc: Special Ops** (`run_special_ops.py`) - A dynamic launcher that allows you to specify a team (e.g., Falcon + Star-Lord for Market Research, or Rocket + War Machine for Infra Upgrades) to run specialized, non-standard missions without triggering the full SDLC.
*   **Intervention: Coulson Routing** (`run_coulson_intervention.py`) - Triggered automatically on exit code 3 (Kickback). Evaluates the failure and routes back to the appropriate phase or halts for Nick Fury.
