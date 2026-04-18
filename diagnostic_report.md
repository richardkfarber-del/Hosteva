# Diagnostic Report: Swarm State & Telemetry Failures

## 1. State Machine 400 Bad Request (FEAT-019 & FEAT-020)
**Root Cause:** 
The transition failure occurred because of a state mismatch between the Redis Event Stream (`swarm:stream:tasks`) and the FastAPI persistent state (`swarm:state:FEAT-*`). 
The previous subagent injected the `REFINEMENT` event directly into the stream without successfully updating the persistent Redis state via the `/state/update` endpoint. As a result, the FastAPI backend defaulted the ticket's `current_state` to `BACKLOG` (or it was explicitly set to `BACKLOG` by `fix_state.py`). 
When Vision completed the refinement and attempted to sync the `BUILDING` state, the FastAPI state machine (`app/api/routes/swarm.py`) evaluated a transition from `BACKLOG -> BUILDING`. According to the `ALLOWED_TRANSITIONS` matrix, `BACKLOG` can only transition to `REFINEMENT` or `BLOCKED`. The illegal jump to `BUILDING` was correctly rejected with a `400 Bad Request`.

**Proposed Fix:**
Ensure that state changes are fully synchronized. When pushing a task into the execution stream (e.g., transitioning it out of the backlog), the system must successfully execute the `POST /state/update` request to lock the state into `REFINEMENT` *before* the `SwarmWorker` acts on it.

## 2. Telegram Webhook Telemetry Failure
**Root Cause:** 
The issue lies in `system/swarm_worker.py` within the `handle_refinement` method. The conditional branch that handles a `"FAILED_REFINEMENT"` output successfully updates the task data and calls `self.sync_fastapi_state(...)`, but it completely omits the `self.send_telegram_alert(...)` function call. Unlike `handle_deploying` or the Coulson audit steps, there is no trigger to dispatch the telemetry payload for failed refinements.

**Proposed Fix:**
Inject the `send_telegram_alert` method directly into the `FAILED_REFINEMENT` branch in `system/swarm_worker.py`:
```python
if output and "FAILED_REFINEMENT" in output:
    data["status"] = TaskState.FAILED_REFINEMENT.value
    self.sync_fastapi_state(ticket_id, TaskState.FAILED_REFINEMENT, {"reason": output})
    self.send_telegram_alert(ticket_id, "vision", TaskState.FAILED_REFINEMENT.value, output) # <-- Add this line
```
