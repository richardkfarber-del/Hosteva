# SPRINT BACKLOG: HOTFIX-001 (Render 500 & UAT)

## Ticket 1: Fix Render 500 Internal Server Error [Pending]
**Feature:** Core Routing
**Task:**
- In `app/main.py`, fix the syntax error in the `read_dashboard` route. The `context` dictionary has a malformed key for `google_maps_api_key`. Restore it to `"google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY", "")`.
- In `app/routers/pricing.py`, update the `TemplateResponse` signature to use keyword arguments. It should be: `return templates.TemplateResponse(request=request, name="pricing.html", context={"request": request})`.

## Ticket 2: Fix UAT False Positives [Pending]
**Feature:** Testing
**Task:**
- In `tests/uat_live_pricing.py`, update the `run_uat()` function to explicitly assert that `response.status == 200` before evaluating the page content for 'stripe' or 'subscribe'. If the status is not 200, it must fail the UAT immediately.
