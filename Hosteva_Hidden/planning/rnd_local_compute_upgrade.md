# Phase 5 R&D Proposal: Local Compute Upgrade for Swarm Tooling
**Author:** Shuri, Head of Platform Engineering (AGENT-26-ENABLEMENT)
**Objective:** Upgrade local Swarm compute capabilities to handle high-complexity back-end API integrations (Sprint 3) with zero cloud API token costs.

## 1. Context & The "Why"
Director Richard gave the directive: "We need to do more local compute. You should have 90% of the system's resources." 
Currently, the Swarm relies on `qwen2.5-coder:7b`. While decent for quick scripts, JARVIS correctly flagged that it chokes on our Sprint 3 backend architecture (OAuth schemas, Celery/Redis queues, complex Airbnb API JSON payload contracts). It hallucinates because it lacks the parameter depth. We need to forge some digital Vibranium to handle this locally.

## 2. Hardware Constraints
- **Host GPU:** RTX 4070 SUPER
- **Total VRAM:** 12GB
- **Target Allocation:** 10-11GB (leaving 1-2GB for OS overhead and context window buffer).

## 3. Model Capability Analysis (Ollama/vLLM Quantized)
We need a model that fits into ~10GB of VRAM while significantly outperforming a 7B parameter model in logic, schema adherence, and context retention.

| Model | Estimated VRAM (Q4_K_M) | Feasibility & Performance |
| :--- | :--- | :--- |
| **`qwen2.5-coder:14b`** | ~8.5 GB | **OPTIMAL.** Fits securely within 10-11GB even with an 8k-16k context window. Massive leap in coding capability and JSON schema adherence over the 7B version. |
| **`codestral:22b`** | ~13 GB | **UNVIABLE (Natively).** Exceeds the 12GB VRAM limit. Would require offloading layers to system RAM, severely degrading generation speed (tokens/sec) and slowing down the Swarm. |
| **`deepseek-coder-v2-lite` (16B MoE)** | ~9 GB | **VIABLE.** Excellent MoE architecture. Very fast, but Qwen 2.5 generally edges it out in strict API/JSON contract adherence. |

## 4. Proposed Solution
**Recommendation:** Upgrade the primary local Swarm backend to **`qwen2.5-coder:14b`** using a **Q4_K_M** or **Q5_K_M** quantization.

*Why?* Just because a 7B model "works" doesn't mean it can't be improved. The 14B Qwen2.5-Coder model will comfortably sit in the RTX 4070 SUPER's VRAM, leave enough room for a healthy context window, and possess the necessary reasoning depth to handle OAuth and Celery/Redis integrations without cloud-tier token costs.

## 5. Next Steps
1. Pull the model via Ollama: `ollama run qwen2.5-coder:14b`
2. Run a baseline JSON schema generation test to verify context retention vs the 7B model.
3. Shift Sprint 3 API integration workloads entirely to this local model.
