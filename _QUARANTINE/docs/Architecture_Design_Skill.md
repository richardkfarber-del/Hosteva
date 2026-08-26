# Architecture Design Skill
## Objective
Establish the immutable structural blueprint, core data models, and API contracts for a feature prior to execution.

## Execution Constraints
- Override local compute defaults: This high-reasoning node MUST be routed explicitly to the Gemini API via GraphBit node-level configurations.
- Designs must conform natively to the existing V3 Pipeline Architecture.
- Output must be valid, highly structured Markdown.

## Mandatory Output Format
1. Component Breakdown: Exhaustive manifest of all modules, interfaces, and files to be created.
2. Data Flow & Sequence Mapping: Step-by-step data lifecycle mapping. You MUST include embedded Mermaid.js or PlantUML sequence diagrams.
3. API Contracts: Complete JSON schemas defining all expected request/payload boundaries.
4. Infrastructure Dependencies: Explicitly list all required external libraries, WASM plugins, or MCP servers.

## Middleware Validation Hook
Before this phase completes, the GraphBit engine will invoke a pre-execution Hook to deterministically compile your C4 models and Mermaid.js diagrams. If syntax errors are detected, the node will fail deterministically, forcing an immediate orchestration loop.