# Pull Request Review Skill

## Objective
Evaluate proposed codebase mutations for structural integrity, security, and strict adherence to defined architectural blueprints within a secure ZeroClaw execution sandbox.

## Execution Constraints
- Resolve the active reviewer persona dynamically from the ZeroClaw session state.
- Do not nitpick stylistic choices unless they violate core project linting rules.
- Focus strictly on logical flaws, race conditions, unhandled exceptions, and missing tests.
- All interactions, comments, and merges MUST be routed out-of-band through the GitHub MCP Server.

## Review Checklist
1. Architecture Alignment: Does the implementation perfectly map to the contracts defined in the architecture_skill.md output?
2. Security & Sandboxing: Are all inputs sanitized? Are secrets completely absent?
3. Performance: Are there N+1 query regressions, unbounded memory allocations, or inefficient loops?
4. Testability: Is the code fully decoupled and testable via automated scripts?

## Mandatory Output Taxonomy
You must format all formal review findings as H3 (###) headings utilizing the strict Request for Comments (RFC) taxonomy below. Open-ended feedback is strictly prohibited.

- ### 🔴 [BLOCKING]: Critical flaws, security breaches, or broken contracts. Requires immediate remediation.
- ### 🟡 [SUGGESTION]: Non-blocking architectural improvements or optimization recommendations.
- ### 🟢 [APPROVAL]: Code meets all standards. Trigger the GitHub MCP Server to execute a squash-merge.
