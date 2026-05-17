# Phase 0: Vanguard Planning (Lua Atomicity & Heartbeats)
**Date:** 2026-04-16
**Goal:** Seal the final concurrency leaks in the Swarm Worker queue.
**Targets:** BUG-015

## Vanguard Consensus & Architectural Alignment

**Iron Man (CTO - Architecture):** 
"The pipeline() alone wasn't enough because it doesn't support conditional execution based on the result of a previous command in the pipeline. We must deploy a raw Redis Lua script. The script will check if the task exists in `swarm:queue:processing` via `lpos`. If it does, it executes `lrem` and `rpush`. If it doesn't (stolen by a sweeper), the script aborts the push, preventing duplication."

**Vision (Data Engineer):** 
"For the false-positive orphans, stamping a timestamp in the JSON payload isn't viable because we'd have to constantly mutate and re-push the JSON string in the queue to update the heartbeat. Instead, when a task enters processing, we will set a separate, volatile Redis key (e.g., `swarm:lock:{ticket_id}`) with an expiration (TTL) of 60 seconds. A lightweight Python `threading.Thread` will run in the background during the LLM HTTP call, sending a heartbeat to extend that TTL every 30 seconds."

**Shang-Chi (Clean Architecture):** 
"The sweeper (`recover_orphaned_tasks`) will then iterate over the processing queue, check if the corresponding `swarm:lock:{ticket_id}` key exists, and ONLY `lrem` / `rpush` the task back to the main queue if the lock has evaporated."

**Hawkeye (Product Owner):** 
"The strategy is sound and the ticket reflects the constraints. BUG-015 is locked."