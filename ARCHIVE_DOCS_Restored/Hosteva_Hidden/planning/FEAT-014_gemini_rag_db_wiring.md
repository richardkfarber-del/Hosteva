# FEAT-014: Gemini RAG Database Wiring & Search Integration

**Domain:** Engineering / Backend
**Feature:** Gemini RAG Database Wiring & Vector Search Integration

**Scenario:** Engineering Implementation
**Given** the backend receives a query intended for the Gemini RAG service
**When** the system queries the PostgreSQL database for relevant context
**Then** it must successfully execute a similarity search utilizing pgvector
**And** Iron Man must implement the security middleware defined in `SPIKE-002` to sanitize inputs against prompt injection
**And** automated `pytest` coverage must be implemented and passing for the new pgvector search logic.
