# UI/UX Specification Skill

## Objective
Extract, validate, and assert interface design specifications directly against remote design endpoints via the Google Stitch MCP Server to ensure pixel-perfect frontend implementation.

## Execution Constraints
- Avoid text-only visual descriptions or LLM-generated styling approximations.
- Connect directly to the Google Stitch MCP Server to pull raw design tokens, typography rules, spacing variables, and exact hexadecimal color codes.
- Prior to frontend code generation, invoke a deterministic validation Script to assert that the proposed implementation properties match the endpoint assets exactly.
- All design extraction MUST target the active project repository: https://stitch.withgoogle.com/projects/6411392088286229161

## Specification Checklist
1. Design Token Alignment: Are the exact hex codes, padding variables, and CSS variables pulled from the remote asset endpoint?
2. Responsive Breakpoints: Are specific layout shifts defined for mobile, tablet, and desktop viewports?
3. Component States: Are hover, focus, disabled, and active states explicitly captured?

## Required Output Format
Output a structured specification containing:
- Asset DNA Payload: The verified JSON token payload extracted from the MCP server.
- Structural Layout Rules: Deterministic CSS/tailwind specifications required for implementation.
- Validation Hook Status: Confirmation that the pre-execution design script successfully passed.