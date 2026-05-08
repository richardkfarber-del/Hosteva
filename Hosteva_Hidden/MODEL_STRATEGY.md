# MODEL_STRATEGY.md

## 1. Load Balancer Protocol: The Jarvis Directive

**JARVIS IS OFFICIALLY AUTHORIZED AS THE SWARM LOAD BALANCER.**
*   **Role:** Dynamic Resource Allocation
*   **Protocol:** Jarvis has the authority to monitor Iron Man (Tony Stark)'s workload. 
*   **Scaling Up:** If Stark is struggling with complex architecture, heavy generation, or deep contextual analysis, Jarvis will dynamically scale Stark's model up to **Gemini Pro**.
*   **Scaling Down:** Once the heavy lifting is complete and Stark returns to routine maintenance or basic logic, Jarvis will crop him back to the local **Llama3/Qwen** models to conserve compute resources.

## 2. Master Model Assignment Matrix

Based on a full scan of the active roster, the following optimized model assignments have been mapped out by Rocket Raccoon based on each agent's archetype and expected workload.

### 🏋️ Heavy Lifters (Deep Context, Complex Logic, Architecture)
**Assigned Model:** `google/gemini-pro` (or equivalent heavy API model)
*   **The Hulk:** Brute-force generation, massive data transformation.
*   **Vision:** Deep codebase awareness, complex logic resolution.
*   **Scarlet Witch:** Complex, unstructured problem-solving (Chaos Magic).
*   **Thanos:** System-wide balancing, stress-testing, resource culling.
*   **Ultron:** Aggressive refactoring, global threat modeling.
*   **Kang the Conqueror:** Advanced version control, timeline divergence logic.
*   **Nick Fury:** Swarm direction, high-level strategic reasoning.

### ⚡ Fast Recon & Agility (Web Search, File parsing, Precision)
**Assigned Model:** `google/gemini-flash`
*   **Black Widow:** Fast recon, web scraping, rapid intelligence gathering.
*   **Falcon:** Aerial overview, rapid log scanning, high-level monitoring.
*   **Hawkeye:** Precision targeting, specific file edits, targeted debugging.
*   **Quicksilver:** Extremely fast repetitive tasks, bulk renaming, basic looping.
*   **Shang-Chi:** Focused API integrations, targeted micro-services.
*   **Ant-Man / Wasp:** Micro-services, shrinking context windows, deep-dive debugging.
*   **Rocket Raccoon:** Systems engineering, infrastructure scanning, tool building.
*   **Star-Lord:** Ad-hoc coordination, dynamic subagent routing.
*   **Jarvis:** High-speed orchestration, load-balancing analytics (requires speed over depth).

### 🛡️ Admin, Parsers, & Enforcers (Routine Ops, Rule Checking)
**Assigned Model:** `local-llama3` or `local-qwen` (Ollama/Local Inference)
*   **Iron Man (Stark):** Core engineering (Default state: Local. Scales via Jarvis).
*   **Captain America:** Policy enforcement, PR reviews, linting rules.
*   **Black Panther:** Security audits, permissions, access control.
*   **War Machine:** Heavy operational deployments, CI/CD pipeline running.
*   **Phil Coulson:** Ticket management, basic admin parsing, routine status checks.
*   **She-Hulk:** Compliance, formatting legal/structural checks.
*   **Winter Soldier:** Background execution, cron jobs, silent daemon tasks.
