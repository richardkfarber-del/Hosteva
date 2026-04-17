# Phase 0: Vanguard Planning (BUG-016)
**Date:** 2026-04-16
**Goal:** Eradicate the final Lua/Heartbeat micro-race conditions in `system/swarm_worker.py`.
**Targets:** BUG-016

## Vanguard Consensus & Architectural Alignment

**Iron Man (CTO - Architecture):** 
"The logic failure was placing the heartbeat thread inside the `try` block *after* we had already started mutating the JSON. We move the `redis_client.set(lock_key, "1", ex=60)` command immediately to the next line after `brpoplpush` returns a task. Then we parse the JSON. If the parsing fails, the DLQ routing MUST use `LUA_SAFE_MOVE` to push the raw string. The script executes atomically on the Redis server, guaranteeing no duplication."

**Vision (Data Engineer):** 
"Agreed. Any operation that touches `swarm:queue:processing` and moves a task must execute through the Lua script, period. A blind Redis pipeline is not atomic if it lacks conditional logic. By forcing the DLQ and `start_time` injection through `LUA_SAFE_MOVE`, we guarantee that if a sweeper steals a task in a 1-millisecond window, the Lua script returns 0 and aborts the `rpush`."

**She-Hulk (CLO - Compliance):** 
"These race conditions compromise the integrity of our audit trail. If a task duplicates, the ledger is falsified. The Lua conditionals must be universal."

**Hawkeye (Product Owner):** 
"The strategy is aligned. Cap's constraints are met. I've locked BUG-016 onto the board."