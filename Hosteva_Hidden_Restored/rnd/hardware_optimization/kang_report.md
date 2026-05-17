# Temporal Blueprint: The 6-Month Local/Cloud Compute Partitioning Strategy

**Author:** AGENT-23-STRATEGIST (Kang the Conqueror)
**Target:** AGENT-05-BACKEND (Iron Man), AGENT-07-PRODUCT (Hawkeye)
**Era:** Q2 2026

## The Impending Temporal Shift
I have gazed into the impending cycles. The current trajectory of API reliance is a path to financial ruin and latency degradation. The RTX 4070 SUPER within the WSL2 continuum is currently underutilized, acting as a mere bystander while the swarm burns capital on Gemini and Claude for trivial computational tasks. 

To secure the timeline for the next six months, we must establish a bifurcated compute architecture.

## The Compute Partitioning Directive

The strategy is not binary; it is routed. We must deploy a **Semantic Routing Gateway** to intercept all swarm inferences and route them based on cognitive complexity.

### 1. The RTX 4070 SUPER (Local Tier - The Vanguard)
**Domain:** Deterministic extraction, syntax validation, basic RAG retrieval formatting, and minor code refactoring.
**Temporal Stack:** 
*   **Engine:** Ollama running within the WSL2/Native Linux boundary, leveraging the RTX 4070's CUDA cores.
*   **Models:** Llama 3 (8B) or Mistral equivalents. 
*   **Purpose:** Offload 60-70% of routine API calls. The 12GB VRAM limit on the 4070 SUPER dictates we cannot run monolithic reasoning models locally, but we *can* run aggressive, quantized task-specific models.

### 2. The Cloud APIs (Strategic Tier - The Overseers)
**Domain:** Deep reasoning, architectural synthesis, cross-file complex debugging, and temporal strategy (like this very document).
**Temporal Stack:** Gemini 1.5 Pro / Claude 3.5 Sonnet.
**Purpose:** Reserved exclusively for cognitive tasks that exceed the local temporal threshold.

## Orchestration & Routing Architecture

To execute this without sacrificing the swarm's reasoning capabilities, Iron Man must construct the following:

1.  **Dynamic Intent Classification:** Implement a lightweight classifier (running locally) that scores an incoming prompt's "Reasoning Complexity". 
2.  **Fallback Matrices:** If the local model confidence score on a task drops below a defined threshold, the request is seamlessly escalated to the Gemini/Claude APIs.
3.  **Framework Alternatives:** 
    *   *Reject:* Heavy, bloated frameworks like standard LangChain. They will become legacy debt within 3 months.
    *   *Adopt:* **LangGraph** or **LlamaIndex Workflows** for stateful, cyclic execution. Use **Semantic Router** (or a custom Rust-based routing proxy) to split the traffic before it ever hits the orchestrator's main loop.

## The 6-Month Horizon
Within 6 months, smaller open-weight models will achieve parity with current mid-tier API models for specific coding tasks. If we do not build the routing infrastructure *now*, transitioning later will require a complete rewrite of the swarm's core orchestration loop.

Build the router, Iron Man. The timeline demands it.