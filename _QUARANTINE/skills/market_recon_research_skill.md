# Market Recon & Research Skill

## Objective
Aggregate external industry trends, competitor API contracts, and newly released open-source tooling, synthesizing actionable intelligence into persistent vector storage without relying on probabilistic assumptions.

## Execution Constraints
- Zero Hallucination: You are strictly prohibited from assuming or fabricating external tool capabilities, pricing tiers, or competitor features. 
- Tool Routing: All external discovery MUST be executed safely out-of-band via verified Web Search and Scraping MCP Servers.
- Persistence: Ingest all verified findings directly into the persistent vector database via the ChromaDB MCP Server to ensure the broader swarm has semantic access to the research.

## Mandatory Research Pipeline
1. Query Execution: Trigger targeted queries through the Web Search MCP tools using explicit keywords defined in the spike or research ticket.
2. Source Verification: Cross-reference scraped payloads. Every extracted claim, API schema, or feature capability must be tied directly to a verified source URL.
3. Data Ingestion: Package the raw text extracts and documentation artifacts, executing batch ingestions into the vector store via ChromaDB MCP tools.
4. Synthesis: Compile a highly structured markdown comparison matrix.

## Required Output Taxonomy
Your final output artifact must provide a clean Markdown document containing:
1. Executive Abstract: A factual summary of the discovered technology or market trend.
2. Comparative Matrix: A structured table evaluating capabilities, compute overhead, licensing models, and integration complexities.
3. Immutable Citations: An exhaustive, bulleted list of all referenced URLs and scraped endpoints.