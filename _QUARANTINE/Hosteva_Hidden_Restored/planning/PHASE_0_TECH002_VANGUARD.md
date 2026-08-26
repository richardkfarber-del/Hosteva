# Phase 0: Vanguard Planning (Redis Streams Migration)
**Date:** 2026-04-16
**Goal:** Migrate `system/swarm_worker.py` and `app/api/routes/swarm.py` to Redis Streams (`XREADGROUP`).
**Targets:** TECH-002

## Vanguard Consensus & Architectural Alignment

**Iron Man (CTO - Architecture):** 
"We are moving from a single `swarm:queue:tasks` List to a Stream named `swarm:stream:tasks`. The API (`swarm.py`) will use `xadd` instead of `rpush`. The Consumer Group will be named `swarm_group`. Each worker will generate a unique UUID for its Consumer Name so it can natively track its own PEL."

**Vision (Data Engineer):** 
"The `recover_orphaned_tasks` function will fire on startup and execute an `XAUTOCLAIM` on `swarm:stream:tasks` for the `swarm_group`. Any message that has been pending for more than 300,000 milliseconds (5 minutes) will be instantly claimed by the new worker and processed. When a worker successfully finishes a task, it just calls `XACK` and the message is permanently deleted from the stream."

**Shang-Chi (Clean Architecture):** 
"We completely strip out the `LUA_SAFE_MOVE` script, the `threading.Thread` heartbeat class, the `start_time` JSON injection, and the regex lock initialization. The `run` loop will just call `xreadgroup(groupname='swarm_group', consumername=self.worker_id, streams={'swarm:stream:tasks': '>'}, block=0)`. It is clean, elegant, and native."

**She-Hulk (CLO - Compliance):** 
"If a task hits 3 strikes, use `XADD` to push it to a separate `swarm:stream:dlq` Stream, and then `XACK` it from the main stream. We maintain a perfect audit trail of all failed executions without clogging the PEL."

**Hawkeye (Product Owner):** 
"The strategy is aligned. Cap's constraints are met. I've locked TECH-002 onto the board."