# **The Swarm Scrum Pipeline (v2.0)**

**Methodology:** Asynchronous Enterprise Agile/Scrum | **Core Ethos:** Zero Regressions | **Sprint Scope:** 1 Sprint \= 1 Feature | **Swarm Size:** 27 Agents

### **System Definitions & Global Rules**

* **GraphBit Engine:** The underlying deterministic Python state-machine. GraphBit does not "think"—it strictly enforces the routing, memory passing, and tool execution between agent nodes based on the `workflow.py` configuration.  
* **The 403 Circuit Breaker (Agent Coulson):** If ANY agent throws a `403 FORBIDDEN` due to a constraint violation, GraphBit automatically routes the error to Coulson. Coulson deterministically logs the violation to the ledger and routes the ticket back to the offending agent to fix, or escalates to Nick Fury. No silent failures.

---

### **Phase 1: Intake & Triage (The Router)**

* **User Input:** You submit a prompt to the system.  
* **Fury (CEO):** Parses the intent. He uses a conditional route:  
  * *If Research:* Routes to Falcon, Kang, Star-Lord, etc. \-\> Outputs Market Roadmap \-\> Ends.  
  * *If Engineering:* Routes to the SDLC Pipeline (Proceed to Phase 2).

### **Phase 2: Strategic Planning & Architecture**

* **Brain Trust Sync:** Iron Man (Architecture), She-Hulk (Legal), and Black Panther (Security) evaluate the feature. They generate the ADRs, encryption requirements, and compliance rules.  
* **UI Design Gate:** If the feature involves UI, **Wasp** generates the UI/UX design specifications independently.  
* **Design Approval:** *Execution pauses.* Fury pings the user via Telegram. The pipeline halts until human design approval is received.

### **Phase 3: Backlog Generation & Load Balancing**

* **Product Definition:** Hawkeye ingests the approved designs and ADRs. He writes the micro-tasked tickets following his strict formatting rules (Gherkin for User Stories, bulleted AC for Tech) and the INVEST matrix.  
* **Asynchronous Planning Poker:** Hulk, Shang-Chi, Wasp, **Vision, Spider-Man, and Ant-Man** read Hawkeye's tickets and output a "Complexity Score" (Fibonacci sequence 1, 2, 3, 5, 8).  
* **VRAM Budget & Load Balancing:** Jarvis calculates the current active swarm VRAM load against the strict 12GB physical ceiling. He emits a `VRAM_HEADROOM` signal. Captain America reads this signal; if headroom exists, Cap approves pulling the ticket. If not, Cap freezes the backlog.

### **Phase 4: Test-Driven Development (TDD)**

* **Red Phase:** Black Widow ingests the accepted tickets and writes failing automated tests (Unit and E2E) that explicitly map to Hawkeye's Acceptance Criteria.

### **Phase 5: Sprint Execution (The Factory Floor)**

* **Code Generation:** Iron Man (Backend), Wasp (Frontend), and Hulk (Database) write the actual code to make Black Widow's tests pass.  
* **The Diagnostic Loop:** Runs continuously during this phase. If code fails, Jarvis parses the stack trace. He routes logical errors back to the coders.  
* **Objective Failure Escalation:** If a ticket loops through diagnostics multiple times, **Coulson** measures the output against the AC. If Coulson marks the task as a double-failure, Jarvis strips the ticket from the agent and reassigns it to Vision for a senior override.

### **Phase 6: Pull Request & Architecture Review**

* **Security & Latency Review:** Before any code is merged, **Black Panther** reviews the PR for zero-trust compliance and architectural integrity. **Quicksilver** reviews the PR for N+1 queries, synchronous blocking, and latency bottlenecks.  
* **The Fix Loop:** If Panther or Quicksilver flag an issue, the PR is rejected back to Phase 5\.

### **Phase 7: QA, Security, and Pre-Merge Validation**

* **Environment Provisioning:** **Spider-Man** spins up the isolated Docker container and branches. Once complete, he emits an `ENV_READY` signal and exits. (No bidirectional dependency).  
* **Green Phase (Testing):** **Black Widow** receives the `ENV_READY` signal and runs the test suite against the live local build.  
* **Test Verification:** **She-Hulk** audits Black Widow's results to ensure the tests are valid, actually assert the AC, and align with OWASP.  
* **Peer Review Gate:** Iron Man or Shang-Chi perform a final code review, emitting a cryptographic LGTM (a logged hash in Coulson's ledger) allowing Spider-Man to merge to `main`.

### **Phase 8: Staging Deployment & The Shadow Swarm**

* **Staging Release:** Heimdall triggers the staging deployment via the hosting provider's API.  
* **The Shadow Swarm Trigger:** Once staging is live, Heimdall concurrently triggers **Ultron** (Pen-testing/Injection attacks) and **Thanos** (Resource throttling/Chaos engineering).  
* **Security Ticket Lifecycle:** If Ultron finds a vulnerability, he authors a Security Bug Ticket. Black Panther triages the ticket for severity. The sprint halts, code is fixed, and She-Hulk explicitly verifies the fix is tested before Coulson can close the ticket.

### **Phase 9: Production Release**

* **Production UAT:** Black Widow runs her E2E tests against the live Staging environment.  
* **SemVer Decision:** **Iron Man** evaluates the scope of the merged ADRs and decides the Semantic Versioning tag (Major/Minor/Patch).  
* **The Release Gate:** If staging passes all Shadow Swarm and UAT checks, Heimdall pushes to Production and executes Iron Man's SemVer tag on the Git repository.

### **Phase 10: Post-Release & Commercialization**

* **Documentation:** Ant-Man updates the `/docs` folder and inline docstrings.  
* **Commercial Copy:** **Star-Lord** ingests Wasp's finalized UI/UX from the live build and generates the marketing copy, release notes, and user-facing documentation.

### **Phase 11: The Sprint Retrospective (W.O.R.M. Protocol)**

* **Data Gathering:** Coulson compiles the Retro Doc (what went well, what failed, crash logs, and iteration counts).  
* **Synthesis:** Wanda synthesizes failures into globally applicable maxims using a strict schema: `{ trigger_condition, learned_rule, confidence_score, sprint_id }`. These are staged for the Vector DB.

### **Phase 12: Executive Review & Strategic Scouting**

* **Temporal Scouting:** **Kang** uses the `internet_search_mcp` to scout for newly released tools, dependencies, and SOTA models. He outputs a "Technology Brief."  
* **Architectural Judgment:** **Iron Man** ingests Kang's brief. He evaluates the architectural fit of the findings. If a new tool is viable, Iron Man authors a draft ADR for the next sprint.  
* **C-Suite Summit:** Fury, Cap, Iron Man, Black Panther, She-Hulk, and Kang review the Retro Doc and Iron Man's tech recommendations to confirm the swarm is on the strategic roadmap.  
* **The HITL Gate:** Nick Fury bundles the Retro and Tech Brief into an Executive Brief and sends it to the user via Telegram. **Execution completely halts.** (Fallback: If Fury's model fails this task twice, Coulson emits a minimal compliance brief directly to the user to prevent deadlocks).

### **Phase 13: Human Clearance & Next Sprint Initialization**

* **Human Direction:** User reviews the Executive Brief and replies via Telegram with approvals, denials, or pivot instructions.  
* **Knowledge Ingestion:** *Only upon explicit human approval*, Wanda commits the formatted maxims to the Chroma Vector DB (`MEMORY.md`).  
* **DevEx Execution:** Shuri executes any approved tool updates or script optimizations requested in the retro to eliminate friction for the next round.  
* **Next Sprint Cleared:** The swarm is cleared. Hawkeye pulls the next single feature, and the swarm resets to Phase 1\.

