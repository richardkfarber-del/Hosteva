# MCP Infrastructure Implementation Plan

## Objective
Properly install, configure, and validate all external Model Context Protocol (MCP) servers required by the V3 Architecture before wiring the GraphBit DAGs.

## Phase 1: Centralized Configuration
- [ ] Create `mcp_config.json` in the root directory.
- [ ] Define connection endpoints, port mappings, and required environment variable keys for: GitHub, Docker, Render, Google Stitch, and ChromaDB.

## Phase 2: ChromaDB Vector Store Setup
- [ ] Verify/Install `chromadb` in the project's virtual environment.
- [ ] Scaffold `mcp_servers/chromadb_mcp.py` to expose `query_vectors` and `ingest_vectors` tools to the swarm.
- [ ] Create `scripts/ingest_history.py` to allow manual/initial population of the vector database from legacy project files.

## Phase 3: External MCP Tool Mappings
- [ ] Ensure the official pre-built MCPs (GitHub, Docker, etc.) can be invoked by the swarm.
- [ ] Map these tools directly into the `scrum_master.py` tool registry so agents can access them dynamically based on their loaded Skills.

## Phase 4: Validation
- [ ] Run a diagnostic script to ping all configured MCP endpoints.
- [ ] Confirm no missing dependencies before moving to the final step (wiring the shattered DAGs).
