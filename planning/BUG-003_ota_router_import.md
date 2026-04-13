# BUG-003: ImportError for `ota_router` in `app/main.py`

## Description
During Gate 1 testing, an `ImportError` prevents the application from starting. The root cause is a namespace mismatch: `app/main.py` attempts to import a router named `ota_router` from `app/integrations/ota_routes.py`, but the `ota_routes.py` file actually defines the router object as `router`.

## Expected Behavior
* The FastAPI application starts successfully without throwing an `ImportError` or `ModuleNotFoundError`.
* `app/main.py` correctly imports the router from `app/integrations/ota_routes.py` using the exact variable name defined in the file (e.g., aliasing `router` to `ota_router` during import, or updating the import statement).
* The OTA integration routes are properly included and registered in the main FastAPI application instance.
* Gate 1 startup tests pass successfully.
## Swarm Review
- **Vision (Architecture):** Approved. The namespace fix aligns with our current routing architecture and doesn't impact database schemas.
- **Iron Man (Execution):** Approved. Clear, concise fix. We update the import statement to match the exported variable or alias it.
- **Black Widow (QA):** Approved. Resolves the critical startup blocker. Gate 1 tests will pass once implemented.
- **Captain America (Agile Lead):** Approved. The bug is cleanly documented with no scope creep.

**Ticket Status: SEALED** - Ready for Execution.
