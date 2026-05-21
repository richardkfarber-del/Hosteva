# Local Inference Recommendations (April 2026)
**Target Hardware:** RTX 5070

## 1. Gemma 4
Google's latest open-weight model family (released April 2, 2026). The sizes include E2B, E4B, 26B, and 31B. For an RTX 5070, the E4B model will run flawlessly at high speeds, while the 26B or 31B models will require heavy quantization (e.g., 4-bit GGUF/AWQ) to squeeze into VRAM.

## 2. Models Beating Qwen 2.5 in the 8B-14B Range
Recent launches in April 2026 show massive strides in the ~10B parameter range:
- **Llama 4 (8B/14B class):** Meta's latest release fits perfectly into the VRAM of an RTX 5070 while providing next-generation intelligence for coding and reasoning tasks, handily beating Qwen 2.5.
- **Qwen 3.6-Plus:** The newest iteration of Qwen significantly surpasses the legacy Qwen 2.5 benchmarks.
- **GLM-5.1:** Another recent April 2026 release that pushes performance above Qwen 2.5 in smaller parameter counts.

## Recommendation for Hosteva
For local progressive web app processing and STR compliance rule checks on the RTX 5070:
1. **Primary Choice:** **Llama 4 (~8B-14B)** or **Qwen 3.6-Plus**. Both offer exceptional speed and beat Qwen 2.5 while easily fitting in VRAM unquantized or lightly quantized.
2. **Alternative:** **Gemma 4 (E4B)** if you need an ultra-fast edge model, or **Gemma 4 (26B)** heavily quantized if you require the highest possible reasoning ceiling and are willing to sacrifice generation speed.