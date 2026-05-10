# QA Test Generation Skill

## Objective
Generate, compile, and deterministically execute repeatable test suites (Playwright/Pytest) based on feature requirements, feeding hard telemetry back into the GraphBit WorkflowContext.

## Execution Constraints
- NEVER probabilistically "imagine" or assume test outcomes. Tests must be physically executed.
- All test environments must be provisioned out-of-band via the Docker MCP Server.
- Tests must execute via the terminal without human intervention, capturing raw stdout/stderr logs.
- Avoid flaky assertions; rely on explicit dynamic waits rather than arbitrary network timeouts.

## Ticket-Driven Test Structures
Your generated test syntax must adapt dynamically to the target ticket classification:
1. User Stories: Utilize Behavior-Driven Development (BDD) syntax strictly written from a third-person perspective (e.g., Given a user is..., When the user..., Then the system...).
2. Tech & Spike Tickets: Validate functionality directly against the bulleted list of Acceptance Criteria.
3. Bug Tickets: Assert state changes specifically against the defined Expected Behavior statement.

## Mandatory Execution Pipeline
1. Provision: Invoke the Docker MCP Server to spin up the required containerized infrastructure.
2. Setup: Initialize pristine database mocks and state baselines.
3. Execute: Trigger the deterministic Testing Script to run the compiled binaries.
4. Assert: Confirm exact payload matches against expected schemas.
5. Teardown: Completely destroy container state to prevent cascading environment pollution.