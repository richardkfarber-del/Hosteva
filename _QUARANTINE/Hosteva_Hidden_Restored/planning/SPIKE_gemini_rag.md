# SPIKE: Gemini RAG Feasibility & Contract (FEAT-012)

## 1. Objective
Assess the feasibility of implementing a Retrieval-Augmented Generation (RAG) system using Google's Gemini API for ordinance compliance analysis, and define the expected API payload contract.

## 2. Vector DB Feasibility
- **Choice:** pgvector (PostgreSQL extension) vs. Pinecone.
- **Decision:** Use pgvector. Hosteva already utilizes PostgreSQL, making pgvector the logical choice to minimize architectural complexity and infrastructure costs.
- **Embedding Model:** Google's `text-embedding-004` will be used to embed ordinance text chunks.

## 3. Gemini API Interaction
- We will query Gemini 1.5 Pro to synthesize compliance answers based on context retrieved from pgvector.

## 4. API Payload Contract

### Request Endpoint: `POST /api/compliance/rag/query`

**Payload:**
```json
{
  "property_id": 123,
  "question": "Are short term rentals allowed in R-1 zoning?",
  "jurisdiction": "Orlando, FL"
}
```

### Response

**Payload:**
```json
{
  "answer": "Yes, short-term rentals are allowed in R-1 zoning in Orlando, FL, subject to obtaining a permit and registering with the city.",
  "sources": [
    {
      "ordinance_id": "ORD-2023-45",
      "section": "10.4.1",
      "snippet": "...short-term rentals are permitted in R-1 residential zones provided the owner registers..."
    }
  ],
  "confidence_score": 0.95
}
```

## 5. Conclusion
Proceed with execution. The RAG architecture is solid, pgvector is ideal, and the API contract is finalized for Iron Man.
