# Sprint 2 Enhancement Plan: V3 Pipeline Hardening & Tooling Pivot

## 1. WHAT We Are Changing

1.  **Aider CLI Integration:** We are replacing the baseline `file_write` tools with **Aider CLI** (`aider-chat`). Aider natively understands git, ASTs, and diff patching.
2.  **Gemini CLI Integration:** We are integrating **Simon Willison's `llm` CLI** (with the `llm-gemini` plugin) and Aider's native Gemini routing for architectural research and diagnostic spikes.
3.  **Strict State Concurrency:** We are implementing Python's `filelock` to wrap `swarm_state.json` reads/writes, preventing race conditions.
4.  **Dynamic Paths & Strike Counters:** Eradicating hardcoded `/home/rdogen/...` paths in favor of environment variables (`os.environ.get("WORKSPACE_ROOT")`). The strike counter will be strictly enforced in the orchestrator.
5.  **Anti-Hallucination Guardrails:** Injecting **Behave** (BDD) and **Hypothesis** (property-based fuzzing) to mathematically force the LLMs to pass real tests.
6.  **Structured Output:** Implementing **Pydantic** and **Instructor** to force agents to output strict JSON schemas instead of markdown strings.

## 2. HOW We Will Implement It

### Tool Installation
We will inject the dependencies into the virtual environment using `uv`:
```bash
uv pip install aider-chat behave hypothesis pydantic instructor filelock llm llm-gemini
```

### Workflow Injection & Guarantees
*   **Phase 5 (Execution):** Instead of Iron Man blindly guessing file edits, `05_execution.py` will programmatically execute: `subprocess.run(["aider", "--model", "ollama/llama3.1", "--message", agent_prompt, "--yes"])`. 
    *   *Guarantee:* By moving the tool execution to the Python `subprocess` level, the agent *cannot* bypass it. The script forces Aider to handle the file modifications on the agent's behalf.
*   **Research Spikes (Diagnostic Reviews):** We will build a `research_spike.py` orchestrator that utilizes the `llm` CLI via subprocess (`llm -m gemini-1.5-pro-latest "prompt"`) or Aider's Gemini routing to scan the codebase and output verified markdown reports.
*   **Scrum Master (State & Strikes):** `scrum_master.py` will be rewritten to use `with FileLock("swarm_state.json.lock"):`. It will catch `sys.exit(1)` from subprocesses and physically increment `state["strike_count"]`.
*   **Testing (Phase 4 & 6):** Hawkeye will write `.feature` files. Phase 6 (Review) will run `behave --format json` and parse the output. If the JSON reports a failure, the pipeline throws a hard `sys.exit(1)`.

## 3. WHY We Are Applying These Changes

*   **Cost & Capability:** Aider provides Claude-level coding autonomy (git diffs, AST parsing) but allows us to route it through local `llama3.1` to maintain our zero-cost mandate. 
*   **Determinism:** Baseline LLMs panic and hallucinate when they fail to use a tool correctly. By abstracting the file writing to Aider and the testing to Behave, we remove the LLM's ability to lie. It either passes the test suite or it fails.
*   **Portability:** Removing hardcoded paths ensures this factory can be cloned and run on any machine or CI/CD pipeline.
