# BUG-001: Remove legacy `celery` dependency from `app/routers/listings.py`

## Description
The `app/routers/listings.py` module currently relies on `celery` for background task execution. This is a legacy dependency that introduces unnecessary overhead and architectural complexity. It needs to be refactored to utilize FastAPI's native `BackgroundTasks` for built-in, lightweight background processing.

## Steps to Reproduce
1. Inspect `app/routers/listings.py`.
2. Note the imports and usage of `celery` for background job execution.

## Expected Behavior
* The `celery` import and all associated task calls are completely removed from `app/routers/listings.py`.
* Background processing in the listings router is handled exclusively via `fastapi.BackgroundTasks`.
* The endpoints execute their background logic successfully without requiring an external Celery worker.
## Swarm Review
- **Vision (Architecture)**: Approved
- **Iron Man (Execution)**: Approved
- **Black Widow (QA)**: Approved
- **Captain America (Agile Lead)**: Approved

**Status**: SEALED
