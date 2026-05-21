# QA Test Generation Skill

## Objective
Generate repeatable test scripts (Pytest/Playwright or raw Python/Bash) based on the groomed ticket to prove the bug exists before the engineers implement a fix (Test-Driven Development).

## Execution Constraints
- Do not use a Docker MCP Server. You are running locally on the filesystem.
- You are a test WRITER, not a test RUNNER. Do not attempt to execute the tests yourself.

## Ticket-Driven Test Structures
Your generated test must adapt dynamically to the target ticket classification:
1. Bug Tickets: Assert state changes specifically against the defined Expected Behavior statement in the ticket.

## Mandatory Execution Pipeline
1. Review the groomed ticket from Phase 3.
2. Write a small test script (e.g., `test_bug_001.py`) into the `tests/` directory using `write_file`.
   - CRITICAL: The test MUST assert the EXPECTED (FIXED) state, not the presence of the bug.
3. Output the plan of the test you wrote as your Phase 4 output, then use `submit_phase_plan` to exit.