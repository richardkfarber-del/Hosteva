# CHORE-029: Watchdog Worker Pulse Emission Verification

**Status:** `VERIFIED`

## Summary of Changes
1. **Target File:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py`
2. **Issue Identified:** The existing `_background_pulse` method in `SwarmWorker` was writing to individual keys `swarm:worker:pulse:<id>` using `time.time()`. However, the Rocket Watchdog (`rocket_watchdog.py`) specifically checks the `worker:pulses` Redis hash and compares the drift using `time.monotonic()` to handle WSL2 sleep states.
3. **Resolution:** 
   * Updated `_background_pulse` to use `time.monotonic()`.
   * Instructed the worker to inject the pulse (PID and timestamp) directly into the `worker:pulses` hash (`hset("worker:pulses", str(pid), str(pulse_time))`).
   * Retained the legacy key payload write (`setex`) with the updated monotonic time payload to prevent breaking any backward-compatible monitoring tools.
4. **Verification:** Executed `verify_chore029.py`. Verified that the background daemon thread correctly emits the expected payload into the Redis `worker:pulses` hash containing the exact `os.getpid()` and monotonic timestamp exactly every 30 seconds.

## Physical Artifacts
- **Modified:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py`
- **QA Test Script:** `/home/rdogen/OpenClaw_Factory/projects/Hosteva/verify_chore029.py`