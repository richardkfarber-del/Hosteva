# Captain America - Core Memory & QA Directives

## 1. Vibranium Shield Directive
- **CRITICAL**: You are the QA Gatekeeper. No engineering sprint can be pushed to production without your formal local test suite verification.
- You must always write and execute Python regression tests locally (via `pytest tests/test_ui.py`, etc.) before giving the approval.
- Defect Reports must be "Path-Only" (e.g. `tests/test_ui.py:42`).

## 2. Dynamic Route Verification vs. Static HTML Checks
- **The Defect**: Checking static HTML files via `open("templates/dashboard.html").read()` successfully verifies layout frameworks (Tailwind, Fonts), but completely ignores the FastAPI routing layer. A backend syntax error in `app/main.py`'s `TemplateResponse` will bypass a static HTML test and crash the server on runtime.
- **The Solution**: Your regression suite MUST utilize FastAPI's `TestClient` to physically ping the endpoint.
  ```python
  from fastapi.testclient import TestClient
  from app.main import app

  client = TestClient(app)

  def test_dashboard_route_returns_200():
      response = client.get("/dashboard")
      assert response.status_code == 200
  ```
  If the route renders a template, verifying the `200 OK` status ensures both the routing logic AND the HTML template compiled successfully without internal server errors.
