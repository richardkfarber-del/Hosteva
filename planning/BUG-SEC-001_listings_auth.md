## BUG-SEC-001: Missing Auth & IDOR in Listings Endpoints

**Severity:** HIGH 🔴
**Component:** `app/routers/listings.py`

**Description:**
The endpoints `/listings/generate/{property_id}` and `/listings/{property_id}/status` do not enforce authentication or verify resource ownership. Any unauthenticated user or authenticated user can trigger a background task for OTA synchronization (`sync_property_to_otas`) or read the listing status of any property by simply passing its `property_id`.

**Reproduction:**
1. Send a POST request to `/listings/generate/ANY_PROPERTY_ID`.
2. Notice the background task triggers successfully without a bearer token or ownership check.

**Expected Behavior:**
* The standard authentication dependency (e.g., `current_user = Depends(get_current_user)`) is injected into the route signatures.
* The system validates that the `current_user.id` matches the owner of the `property_id` retrieved from the database before queuing the `BackgroundTasks` or returning status details.
