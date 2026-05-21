# The Hosteva Swarm: GraphBit SCRUM Architecture

## The Problem: The GraphBit DAG Limitation
The GraphBit framework strictly enforces a Directed Acyclic Graph (DAG) architecture. It mathematically forbids cycles (nodes routing backward to previous nodes). Attempting to wire a kickback loop *inside* a single GraphBit workflow causes a hard `RuntimeError` and crashes the pipeline.

## The Solution: External Orchestration
To satisfy both GraphBit's DAG constraints and the team's SCRUM requirements (kickbacks, retries, multi-agent reviews), the architecture is split into two layers:

1. **The Master Orchestrator (`scrum_master.py`)**: A standard Python script that manages the state, phase transitions, and cyclic SCRUM loops. It executes the phases as isolated subprocesses.
2. **The Phase Workflows (`scrum_pipelines/*.py`)**: 13 isolated, strictly linear GraphBit workflows. Each workflow represents a single phase of the SCRUM pipeline. Because they are linear, they perfectly comply with GraphBit's DAG rules.

## The Kickback & Failsafe Mechanism (The 3-Strike Rule)
When a phase fails (e.g., Phase 5 Execution fails tests):
- The phase script outputs a `FAIL` signal and exits with code 1.
- The `scrum_master.py` orchestrator catches the failure.
- The orchestrator increments the `strike_counter`.
- The orchestrator triggers a Kickback Phase (e.g., Jarvis parsing errors) to generate a state file for the coders.
- The orchestrator reignites Phase 5 with the new state.
- **The Rocket Raccoon Circuit Breaker**: If the `strike_counter` reaches 3, the orchestrator halts the loop, triggers `rocket_failsafe.py` to log the catastrophic failure to the ledger, and shuts down the entire pipeline. No infinite loops.