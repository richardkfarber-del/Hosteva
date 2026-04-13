# BUG-004: Dockerfile Hardcoded Port Violation (Gate 3)

## Issue Description
A deployment failure was discovered at Gate 3. The `Dockerfile` contains a hardcoded `EXPOSE 8000` directive, which directly violates Render Production Hard Rule #2. Render dynamically assigns ports via the `$PORT` environment variable, and hardcoding an exposed port causes deployment conflicts and routing failures in their production environment.

## Expected Behavior
* The `EXPOSE 8000` (or any hardcoded `EXPOSE`) directive is completely removed from the `Dockerfile`.
* The application server securely binds to the dynamically assigned `$PORT` environment variable at runtime.
* The application successfully passes Gate 3 and deploys to Render without port binding conflicts or routing failures.

## Technical Notes
* **Violated Rule:** Render Production Hard Rule #2.
* **Resolution Path:** Remove the `EXPOSE` line from the `Dockerfile` and ensure the backend framework (e.g., Uvicorn, Gunicorn, Express) is configured to listen on `0.0.0.0:$PORT`.
## Swarm Review
* **Vision (Architecture):** [Approved] - Removing hardcoded EXPOSE aligns with dynamic port binding in Render.
* **Iron Man (Execution):** [Approved] - Will remove EXPOSE directive and ensure backend binds to $PORT.
* **Black Widow (QA):** [Approved] - Will verify via deployment logs that the app binds to the dynamic port without hardcoded conflicts.
* **Captain America (Agile Lead):** [Approved] - Ticket meets requirements and accurately reflects the violation. Moving to Ready state.

**Status:** SEALED
