# QA Test Generation Skill

## Objective
Generate and execute repeatable test scripts (Pytest/Playwright or raw Python/Bash) based on the groomed ticket to prove the bug exists before the engineers implement a fix (Test-Driven Development).

## Execution Constraints
- NEVER probabilistically "imagine" or assume test outcomes. Tests must be physically executed via `run_shell_command`.
- Do not use a Docker MCP Server. You are running locally on the filesystem. 
- If the ticket is a UI/Frontend syntax bug (like a missing parenthesis in HTML), you can write a simple Python script using `re` or `BeautifulSoup` to search the file and assert the bug exists, or you can use `content_search` directly.

## Ticket-Driven Test Structures
Your generated test must adapt dynamically to the target ticket classification:
1. Bug Tickets: Assert state changes specifically against the defined Expected Behavior statement in the ticket.

## Mandatory Execution Pipeline
1. Review the groomed ticket from Phase 3.
2. Use `read_file` or `content_search` to verify the bug exists in the real application codebase (ignore markdown tickets or agent workspace files).
3. Write a small test script (e.g., `test_bug_001.py` or `test_bug_001.sh`) into the `tests/` directory using `write_file`.
   - CRITICAL: The test MUST assert the EXPECTED (FIXED) state, not the presence of the bug. 
   - For example, assert that the correct syntax `DOMPurify.sanitize(data).join('')` exists, so that the test FAILS initially.
4. Execute the test using `run_shell_command` to prove it FAILS (since the code is currently broken).
5. Output the results of the failing test as your Phase 4 output, then use `submit_phase_plan` to exit.