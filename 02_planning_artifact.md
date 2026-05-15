BUG-002: Persistent Broken Logo

Description: Fix the broken image links by replacing hardcoded HTML paths (e.g., `<img src="/static/img/hosteva_logo.png">`) with proper Jinja2 dynamic routing globally across the repository so the logo renders correctly regardless of the route depth.

Expected Behavior: The logo should render correctly on all pages, using Jinja2 `url_for`.

--- ARCHITECTURE NOTES (Iron Man) ---
N/A - No impact on my domain

--- DATA/SCHEMA NOTES (Vision) ---
N/A - No impact on my domain

--- BACKEND NOTES (The Hulk) ---
N/A - No impact on my domain

--- SECURITY NOTES (Black Panther) ---
```
**Phase 1: Identification and Documentation**

1. **Identified Files:**
   - `./app/templates/dashboard.html`
   - `./Hosteva_Hidden/templates/dashboard.html`
   - `./ARCHIVE_DOCS/Hosteva_Hidden/templates/dashboard.html`

2. **Current State:**
   Each file contains a hardcoded path to the hosteva_logo.png file.

3. **Target State:**
   Replace each instance of `<img src="/static/img/hosteva_logo.png" alt="Hosteva Logo" class="h-20 w-20 object-contain" onerror="this.onerror=null; this.src='https://placehold.co/200x80/006576/ffffff?text=Hosteva';">` with `<img src="{{ url_for('static', filename='img/hosteva_logo.png') }}" alt="Hosteva Logo" class="h-20 w-20 object-contain" onerror="this.onerror=null; this.src='https://placehold.co/200x80/006576/ffffff?text=Hosteva';">`.

---
**Phase 2: Implementation**

1. **Step 1:** Open `./app/templates/dashboard.html` and replace the hardcoded path with the Jinja2 template.
2. **Step 2:** Open `./Hosteva_Hidden/templates/dashboard.html` and replace the hardcoded path with the Jinja2 template.
3. **Step 3:** Open `./ARCHIVE_DOCS/Hosteva_Hidden/templates/dashboard.html` and replace the hardcoded path with the Jinja2 template.

---
**Phase 3: Testing**

1. **Verify Changes:**
   - Load each page in a web browser to ensure that the logo renders correctly.
   - Check for any errors or issues related to the image loading.

2. **Document Results:**
   - Document any observed changes and verify that the logo is now rendering as expected.

---
**Phase 4: Review and Verification**

1. **Code Review:**
   Ensure that the changes are properly implemented and do not introduce new vulnerabilities.

2. **Final Verification:**
   Confirm that all instances of the hardcoded path have been replaced with the Jinja2 template.
```

--- FRONTEND NOTES (Wasp) ---
N/A - No impact on my domain

