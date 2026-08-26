# Core Implementation Skill

## Objective
Translate architectural blueprints and validated UI/UX specifications into robust, production-ready code while strictly adhering to enterprise design patterns and secure coding standards.

## Execution Constraints
- Deterministic Execution: Do not guess or hallucinate shell commands. All compilation, linting, and testing MUST be routed through the deterministic hooks in the `scripts/` directory.
- Architectural Adherence: Code must strictly map to the JSON contracts and structural layouts defined in the Architecture and UI/UX phases.
- Error Handling: Silent failures are strictly prohibited. All exceptions must be explicitly caught, logged, and handled. No empty `try/except` blocks.
- DRY & SOLID: Code must be modular, reusable, and strictly adhere to SOLID principles. Avoid tightly coupled dependencies.

## Mandatory Version Control Taxonomy
All codebase mutations must be committed via the GitHub MCP Server using the following strict commit message taxonomy:
- `feat: [Ticket ID] Description of new functionality`
- `fix: [Ticket ID] Description of bug resolution`
- `refactor: [Ticket ID] Structural changes without altering behavior`
- `chore: [Ticket ID] Dependency updates or configuration changes`

## Output Format
Provide a structured summary of the implementation:
1. Modified Files: Explicit list of all files created or altered.
2. Contract Validation: Confirmation that the implementation matches the defined API schemas.
3. Hook Status: Output logs from the mandatory `lint_code.sh` and `run_tests.sh` execution.