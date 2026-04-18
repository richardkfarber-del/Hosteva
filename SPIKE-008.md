# SPIKE-008: Swarm Pipeline Overhaul & Post-Deployment Lifecycle

## 1. Objective
Redesign the FastAPI/Redis State Machine (`app/api/routes/swarm.py` and `swarm_worker.py`) to enforce the new 13-step pipeline. This includes shifting Security/Legal reviews left, eliminating passive dead-end states, mapping the SPIKE review gate, and implementing strict post-deployment approval tollgates.

## 2. Pipeline State Transitions

### Phase 1: Planning, Refinement & Compliance (Shift-Left)
*   **Step 1 (BACKLOG):** Ticket generated. Auto-transitions to `REFINEMENT`.
*   **Step 2 (REFINEMENT & COMPLIANCE):** 
    *   *Fix:* Must dynamically spawn the FULL Vanguard PLUS the Threat Council AND Heimdall (Black Panther, She-Hulk, Falcon, Kang, Iron Man, Vision, Heimdall).
    *   *Rule:* Security and Legal MUST review and approve constraints before any code is built. Agents outside their domain must explicitly PASS.
    *   *Gate:* Captain America Definition of Ready veto. Jarvis assigns tier.

### Phase 2: Execution & Audit
*   **Step 3 (BUILDING):** Execution Squad builds code/tests.
*   **Step 4 (AUDITING):** Coulson verifies physical hashes/diffs.

### Phase 3: Pre-Deployment QA & Approval
*   **Step 5 (TESTING):** Local headless QA (Cap/Widow).
*   **Step 6 (PENDING_APPROVAL):** **[HARD HALT]** Secretary approves final UI/UX before launch. 
    *   *(Note: If the ticket is a SPIKE, it routes to `SPIKE_REVIEW` here instead of `PENDING_APPROVAL`)*

### Phase 4: Deployment & Post-Prod Lifecycle
*   **Step 7 (DEPLOYING):** Heimdall pushes to Render.
*   **Step 8 (PROD_DEPLOYED):** Deployment successful.
*   **Step 9 (POST_PROD_QA):** QA team runs headless tests natively against the live production environment.
*   **Step 10 (RETROSPECTIVE):** All sprint agents submit feedback to a master report.
*   **Step 11 (EXECUTIVE_REVIEW):** **[HARD HALT]** Awaiting Secretary and Director review of the Retro report.
*   **Step 12 (DEEP_WRITE_DONE):** Wanda is triggered to append permanent memory *only* after live Secretary feedback is provided. Ticket officially closed.

## 3. Structural Fixes & Loop Prevention
*   **The Dead-End Fix:** `FAILED_REFINEMENT` and `REJECTED` are reprogrammed as active routing states. They auto-route the payload back to Hawkeye (for Refinement failures) or the Execution Squad (for Build failures), and ping the Secretary via Telegram.
*   **Circular Loop Prevention (The 3-Strike Rule):** To prevent endless loops between `REJECTED` and `BUILDING` or `REFINEMENT`, a global state counter is enforced. If a ticket is rejected 3 times, it routes to `FAILED_ESCALATED` **[HARD HALT]**, requiring manual Secretary intervention.
*   **SPIKE_REVIEW Mapping:** 
    *   If ticket type == `SPIKE`, after `TESTING` (or Refinement if no code is required), it routes to `SPIKE_REVIEW` **[HARD HALT]**.
    *   If Secretary Approves -> `DONE`.
    *   If Secretary Rejects -> Routes back to `REFINEMENT` (Strike counter increments).

## 4. Definition of Done
- `swarm_worker.py` logic updated to spawn the Vanguard + Threat Council in Refinement.
- `app/api/routes/swarm.py` State Dictionary updated with all new steps, `SPIKE_REVIEW`, and the 3-Strike Escalation rule.
- All dead-end passive states eliminated.