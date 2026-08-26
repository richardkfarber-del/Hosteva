# GraphBit Research & Architecture Document

## Core Findings on GraphBit

1. **Strict DAG Enforcement:** GraphBit mathematically forbids cycles (loops) in the workflow graph. Even if you attempt to use `workflow.set_graph_metadata('allow_cycles', True)`, the underlying Rust engine will throw a `RuntimeError: Graph error: Workflow graph contains cycles` during validation. 
   * **Conclusion:** You CANNOT route a node backwards (e.g., Tester -> Coder) inside the graph itself.

2. **Tool Assignment:** A node can only execute tools if they are explicitly passed via the `tools=[...]` array during instantiation. In our previous 28-node graph, the Coder nodes (`Iron Man`, `Wasp`) were never assigned tools. They were physically incapable of writing code or running shell commands, resulting in a pure text-generation roleplay.

3. **Routing Syntax:** Router nodes in GraphBit must use the explicit 2-argument `.connect()` syntax. You cannot pass an array of targets. 

## The SCRUM Solution (Linear Workflows with External State)

Because GraphBit strictly enforces linear Directed Acyclic Graphs (DAGs), we cannot build a continuous, infinite SCRUM loop entirely inside a single `Workflow` object. 

**The Architecture:**
We must wrap the linear GraphBit workflow inside a standard Python `while` or `for` loop to handle the "kickbacks."

1. **The Graph (Linear):** Planner -> Coder (with tools) -> Tester (with tools) -> END.
2. **The Loop (External):** The Python script executes the graph. It reads the final output of the `Tester` node. If the Tester outputs `FAIL`, the Python script captures that output, feeds it into a `feedback` variable, and re-instantiates the graph from the beginning.

This satisfies both the GraphBit DAG limitation and the SCRUM requirement for iterative self-improvement and kickbacks.

## Current Status
- The massive 28-node roleplay graph has been backed up to `workflow_28node_backup.py`.
- `workflow.py` has been completely rewritten to use the exact Planner -> Coder -> Tester loop described above, with actual `run_shell_command`, `write_file`, and `read_file` tools assigned to the Coder.
- The correct Render 500 and UAT False Positives bugs have been restored to `SPRINT_BACKLOG.md`.