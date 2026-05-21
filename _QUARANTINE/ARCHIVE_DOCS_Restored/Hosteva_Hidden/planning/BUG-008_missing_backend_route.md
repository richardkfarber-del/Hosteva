# BUG-008: Missing Backend Route for Compliance Chat UI
**Domain:** Engineering / Backend
**Description:** The production and local staging environments are returning 404 Not Found for the frontend route `/compliance_chat`. Additionally, the API endpoint `POST /api/compliance/rag/query` required by the frontend JavaScript is missing in `app.main` and router definitions. This prevents the Gemini RAG Chat UI from functioning.
**Trigger:** Gate 4 Production UAT Failure (Rocket Trigger +1)
