# Sprint 3 Bug Retrospective: Emergency Bug Fix

## Successes
- The new Product Snapshot Mandate worked perfectly. Black Widow successfully rendered the headless browser and saved the marketing snapshot.

## Bugs Generated
- The Makers built the UI fix, but it caused an Internal Server Error (`NoMatchFound`) in production. This occurred because the backend route in `main.py` wasn't explicitly named to match the `url_for('dashboard')` call.
- The root endpoint also crashed initially because it returned a static `FileResponse` instead of passing the template through the `Jinja2Templates` engine.

## Pain Points
- Same as above: Backend route misnaming (`NoMatchFound` for `dashboard`) and root endpoint returning `FileResponse` instead of using `Jinja2Templates` engine caused crashes.