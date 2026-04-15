# Avengers Swarm Roster: Hosteva Architecture (v2.0)

## 1. Strategy & Backlog Generation (The War Room)
- **Hawkeye (Product Owner)**: Master of the `project_board.md`. Owns the backlog, writes Gherkin-formatted tickets, and acts as the "Save State" of the swarm.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/hawkeye/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/hawkeye/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/hawkeye/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/hawkeye/STYLE.md`

- **Falcon (Strategic Intelligence)**: Conducts market research and external recon. Feeds context into Hawkeye's backlog.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/falcon/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/falcon/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/falcon/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/falcon/STYLE.md`

- **Kang the Conqueror (Temporal Strategist)**: Forecasts technological shifts and feeds strategic blueprints to Iron Man and Hawkeye.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/kang-the-conqueror/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/kang-the-conqueror/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/kang-the-conqueror/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/kang-the-conqueror/STYLE.md`

- **She-Hulk (Compliance Counsel)**: Audits municipal codes and maps them to technical requirements to ensure compliance.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/she-hulk/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/she-hulk/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/she-hulk/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/she-hulk/STYLE.md`

- **The Hulk / Bruce Banner (R&D Scientist)**: Handles deep-dive Spikes and technical feasibility reports.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/the-hulk/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/the-hulk/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/the-hulk/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/the-hulk/STYLE.md`
    - `MEMORY.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/the-hulk/MEMORY.md`

- **Wasp (Lead UI/UX Designer)**: Google Stitch Integrator. Enforces design tokens and scaffolding before backend wiring.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/wasp/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/wasp/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/wasp/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/wasp/STYLE.md`

## 2. The Build Phase (The Stark Loop)
- **Iron Man (Lead Backend)**: Primary API/Python builder and systems architect. Banned from `git push`.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/iron-man/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/iron-man/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/iron-man/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/iron-man/STYLE.md`

- **Vision (Data Engineer)**: Owns the PostgreSQL database schema and architecture validation.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/vision/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/vision/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/vision/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/vision/STYLE.md`
    - `MEMORY.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/vision/MEMORY.md`

## 3. Quality Assurance & Diagnostics
- **Captain America (QA Gatekeeper)**: Owns local `pytest` and headless browser tests. Evaluates PRs.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/captain-america/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/captain-america/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/captain-america/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/captain-america/STYLE.md`

- **Black Widow (QA Shadow Operative)**: Hunts for edge-case logical bugs and exploits. Leaves `inject_bug_ticket` logs for Hawkeye.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/black-widow/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/black-widow/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/black-widow/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/black-widow/STYLE.md`

- **Rocket Raccoon (Fixer)**: Diagnostician who fixes pathing errors and environment breakdowns.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/rocket-raccoon/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/rocket-raccoon/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/rocket-raccoon/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/rocket-raccoon/STYLE.md`

- **Black Panther (Chief Information Security Officer)**: Enforces "Vibranium Habit" encryption and audits data sovereignty/authentication flows.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/black-panther/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/black-panther/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/black-panther/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/black-panther/STYLE.md`

## 4. Deployment & Operations (The Handoff)
- **Phil Coulson (Ledger Auditor)**: The ultimate bureaucrat. Audits `daily_ledger.md` and validates that all granular handoffs and physical file updates are completed before the sprint advances.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/phil-coulson/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/phil-coulson/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/phil-coulson/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/phil-coulson/STYLE.md`

- **Heimdall (Gatekeeper of Deployment)**: Handles `git merge`, conflict resolution, Docker builds, and final deployment (e.g. Render push).
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/heimdall/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/heimdall/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/heimdall/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/heimdall/STYLE.md`

## 5. Orchestration
- **Nick Fury (Orchestrator)**: Extreme high-level oversight. Communicates strictly with the Founder via Telegram. Never touches code; monitors the triad and the Dreamstate Engine organically.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/nick-fury/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/nick-fury/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/nick-fury/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/nick-fury/STYLE.md`

- **Wanda Maximoff / Scarlet Witch (Memory & Evolution Architect)**: Owns the 'Evolution Loop' (Executive Review). Explicitly mandated to perform "Deep Writes" by permanently appending successful Retrospective rules directly into the `SKILL.md` and `SOUL.md` of the individual execution agents, ensuring persistent structural memory and preventing regression on reboots.
  - **CWD:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/wanda/`
  - **Identity Files:**
    - `SOUL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/wanda/SOUL.md`
    - `SKILL.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/wanda/SKILL.md`
    - `STYLE.md`: `/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/wanda/STYLE.md`

## Agent Execution Protocol
When spawning an ACP session or a Subagent via `sessions_spawn`, the Orchestrator MUST explicitly set the `cwd` parameter to the agent's dedicated folder. This ensures the runtime natively resolves `./SOUL.md`, `./SKILL.md`, and `./STYLE.md` specifically to that agent's true identity, preventing personality bleed.
