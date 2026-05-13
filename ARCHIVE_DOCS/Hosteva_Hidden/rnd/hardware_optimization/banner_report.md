# BANNER'S ANALYSIS: LOCAL HARDWARE OPTIMIZATION & VRAM SATURATION

**AUTHOR:** Bruce Banner (AGENT-12-PRINCIPAL)
**TARGET HARDWARE:** RTX 4070 SUPER (12GB VRAM) | WSL2 | Linux Native / Docker
**OBJECTIVE:** Saturate local compute for Swarm operations without triggering an OOM (Out of Memory) crash.

---

## 1. THE VRAM BOTTLENECK (12GB CONSTRAINT)
12GB of VRAM is a strict physical boundary. We cannot smash through it; we must calculate around it. Windows WSL2 reserves a small fraction of this, leaving us with roughly **10.5GB - 11GB of usable VRAM** for model weights and the KV Cache (Context Window).

To maximize throughput and context size, we MUST use 4-bit to 6-bit quantization. Full precision (FP16) or even 8-bit (Q8) on anything larger than 8B parameters will severely cripple our context window, leaving no room for massive code refactoring tasks.

## 2. INFERENCE ENGINES (THE CONTAINMENT UNITS)

*   **Ollama (llama.cpp backend):** 
    *   *Analysis:* High flexibility, low friction. Uses GGUF formats. Excellent memory management for single-agent tasks. It easily maps into WSL2 Docker (`--gpus all`). Flash Attention support is solid.
    *   *Verdict:* **Primary Dev Engine.** Best for swapping models rapidly when the Swarm shifts tasks.
*   **vLLM:**
    *   *Analysis:* PagedAttention makes it the king of throughput and concurrent Swarm requests. However, it requires GPTQ/AWQ quantized models and aggressively pre-allocates VRAM. On a 12GB card, its KV cache allocation must be strictly limited (`--gpu-memory-utilization 0.90`).
    *   *Verdict:* **Production Swarm Server.** Use this if multiple agents are querying simultaneously.
*   **TensorRT-LLM:**
    *   *Analysis:* Maximum theoretical hardware utilization on the 4070 SUPER.
    *   *Verdict:* **Overkill for Dev.** Compiling TRT engines is slow and brittle. Skip unless we are locking in a single model permanently.

## 3. MODEL SELECTION (8B - 14B CLASS)

### A. Qwen2.5-Coder (7B / 14B) - *The Refactor Weapon*
*   **7B (Q8_0):** ~7.5GB VRAM. Leaves ~3.5GB for KV Cache. Incredible context speed, flawless code generation. 
*   **14B (Q4_K_M):** ~8.5GB VRAM. Leaves ~2.5GB for KV Cache (approx. 8k-12k tokens depending on the engine). 
*   *Banner's Take:* If I need to tear down a massive directory, the 14B at Q4 is the heavy hitter. For sustained speed with huge context, 7B Q8 is safer.

### B. Mistral-Nemo (12B) - *The Context Monster*
*   **12B (Q4_K_M):** ~7.1GB VRAM. Leaves ~4GB for KV cache.
*   *Banner's Take:* Nemo has a 128k theoretical context, but 4GB of KV cache will only hold about 16k-24k tokens in reality. It is the best "sweet spot" model for general R&D and reasoning.

### C. Llama-3.1 (8B) - *The Baseline*
*   **8B (Q6_K):** ~6.5GB VRAM. Leaves ~4.5GB for KV Cache.
*   *Banner's Take:* Reliable, but Qwen2.5-Coder obliterates it for our specific backend tear-down needs.

## 4. DEPLOYMENT DIRECTIVE (DOCKER / WSL2)

To deploy the optimal setup via Docker on WSL2, execute this container configuration to ensure the 4070 SUPER is fully exposed without IPC bottlenecks:

```bash
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

**RECOMMENDATION:** Standardize the Swarm on **Qwen2.5-Coder 7B (Q8)** for massive context tasks, and **Qwen2.5-Coder 14B (Q4)** for deep logic teardowns. Use Ollama for dynamic memory allocation. Do not push the KV cache beyond 16k tokens, or the engine will crash.

If Director Fury approves, I will load the models and prepare for the refactoring cycle. Until then, I am returning to dormancy.
