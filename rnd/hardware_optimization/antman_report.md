# Subatomic Hardware Optimization Report
**Author:** Scott Lang (AGENT-13-MICRO)
**Objective:** Shrink host OS overhead to leave maximum RAM/VRAM for AI Inference (RTX 4070 SUPER).

Look, guys, I know we've got an RTX 4070 SUPER, which is basically the equivalent of having Giant-Man on standby. But if we let WSL2 and Docker bloat up, we're suffocating the big guy before he even gets to work. We need to shrink the environment down to the subatomic level. Here's how we keep the host OS lean so the swarm's AI inference has all the memory it needs.

## 1. WSL2 `.wslconfig` Tuning
WSL2 is incredibly greedy. It will dynamically consume all your available RAM if you let it, starving the Windows host and severely limiting the contiguous memory needed for loading large models into VRAM. We need to put a hard cap on it.

Create or update `C:\Users\<YourUsername>\.wslconfig` (on the Windows side) with this:

```ini
[wsl2]
# Cap memory to leave room for the host OS and AI model loading (adjust based on total RAM, e.g., 12GB for a 32GB system)
memory=12GB 
# Limit CPU cores to leave host threads available for Orchestration
processors=6
# Prevent aggressive swapping which kills SSD IO and slows inference to a crawl
swap=2GB
# Reclaim memory from WSL2 when not actively used
pageReporting=true
```
*(Remember to run `wsl --shutdown` after applying!)*

## 2. Docker Container Pruning & Shrinking
Docker loves to hoard. Unused images, dangling build caches, stopped containers—it's like a messy closet. Let's shrink it down.

**The Quantum Prune (Run this regularly to clear disk space/cache):**
```bash
docker builder prune -a -f
docker system prune -a --volumes -f
```

**Dockerfile Enforcement (My Personal Crusade):**
*   **NO `ubuntu` base images.** Stop it. Use `alpine` or `distroless`. 
*   **Multi-stage builds:** Only compile in the build stage, copy ONLY the compiled binaries/artifacts to the runtime stage.
*   A 2GB Node container is a crime. We aim for < 150MB.

## 3. Dependency & Payload Optimizations
If we are running the Swarm natively or in tiny containers, our payload has to be microscopic.
*   **Tree-shaking:** If we're deploying frontend/Node.js, bundle it with Vite/esbuild and strip out unused exports.
*   **Drop bloated NPM packages:** Swap `moment.js` for `date-fns` (or just native JS). 
*   **Production installs only:** Always use `npm ci --omit=dev` for the final runtime payload. Dev dependencies do not belong in the Quantum Realm.
*   **Offload AI:** Let the native Ollama handle the heavy lifting directly on the 4070. Keep the microservices strictly for routing, logic, and state.

Keep it small, keep it fast.
