# EXECUTIVE OVERRIDE: PIPELINE OVERHAUL DIRECTIVE (SPIKE-008)

**TO:** Captain America (QA/DoR Gatekeeper), Hawkeye (Product Owner)
**FROM:** Nick Fury (Director), Richard Farber (Secretary)
**DATE:** 2026-04-18

## MISSION PARAMETERS
The current Swarm State Machine (`swarm_worker.py` & `app/api/routes/swarm.py`) has critical structural flaws and is missing essential post-deployment tollgates. The sprint is HALTED. 

Captain America: You are to lead the team in drafting a comprehensive SPIKE ticket (`SPIKE-008`) to redesign the pipeline. Once the SPIKE is complete, it will be delivered to the Secretary for approval before any code is written.

## PIPELINE FLAWS TO ADDRESS
1. **The Vanguard Bypass:** `REFINEMENT` currently hardcodes `vision` only. It must be patched to spawn the entire Vanguard team for review.
2. **The Parking Lot Dead-Ends:** `REJECTED` and `FAILED_REFINEMENT` are passive states that silently drop tasks. They must automatically route back to Hawkeye/Cap or emit a hard alert.

## NEW PIPELINE ARCHITECTURE (STEPS 8-13)
The post-deployment pipeline must be completely rewritten to follow this exact sequence:

*   **Step 8 (Deployment):** Heimdall deploys to production. This NO LONGER triggers Wanda's Deep Write.
*   **Step 9 (Post-Prod QA):** The QA team tests the *live production environment* using headless browsers and executes test cases directly in prod to validate the deployment.
*   **Step 10 (Retrospective Phase):** The entire Swarm team generates individual feedback reports based on the sprint. This feedback is compiled into a master report and delivered to Fury and the Secretary. 
*   **Step 11 (Executive Review Phase):** The system transitions to Executive Review and triggers a **HARD HALT** awaiting Secretary Approval.
*   **Step 12 (Security & Legal Review Phase):** After Exec Review, the system transitions to Security/Legal Review and triggers another **HARD HALT** awaiting Secretary Approval.
*   **Step 13 (The Deep Write):** Only after the Secretary has reviewed the Retro, Exec, and Security/Legal feedback AND provided live feedback will Wanda be triggered to perform the final Deep Write.

**ACTION REQUIRED:**
Hawkeye, draft this as SPIKE-008. Cap, validate the DoR and map out the exact state transitions required for the new FastAPI backend. Do not begin building until Secretary Farber signs off on the SPIKE.
## NEW MANDATE: SPIKE TICKET GATE
*   **Spike Review Halt:** The completion of ANY `SPIKE` ticket must result in a **HARD HALT**. The output/findings of the Spike must be delivered directly to the Secretary and Director Fury for manual review and approval before any subsequent tickets derived from that Spike are allowed to proceed.
