# Hosteva Project Board

## Current Focus Target
Regression Sprint (UI/UX Audit & Bug Fixes)

## Active Tickets

### [BUG-001] dashboard.html Template Literal Leak
**Expected Behavior:** 
* Raw JavaScript text must no longer be visible under the Geospatial Parcel Map.
* The map must continue to function normally without leaking JS into the DOM.
*Assignments:* Wasp / Iron Man (Fix), Captain America (QA)

### [BUG-002] Persistent Broken Logo
**Expected Behavior:**
* The logo must render correctly on all major views utilizing the correct asset path.
*Assignments:* Wasp (Fix), Captain America (QA)

### [BUG-003] CSS Duplication in /dashboard
**Expected Behavior:**
* Duplicate CSS classes and redundant stylesheets are removed.
* The dashboard layout remains visually correct while reducing the CSS payload size.
*Assignments:* Wasp (Fix), Captain America (QA)

### [BUG-004] Silent Failure on Empty Form Submit (/wizard)
**Expected Behavior:**
* Attempting to submit an empty form on the `/wizard` UI displays clear validation error messages to the user and prevents submission.
*Assignments:* Iron Man / Wasp (Fix), Captain America (QA)

## Backlog
*No additional tickets. Full focus on the active regression sprint.*

## Next Action Upon Restart
NEXT_ACTION_UPON_RESTART: Wasp and Iron Man to begin executing fixes on BUG-001 through BUG-004. Captain America to verify Expected Behaviors are met upon completion of each fix.