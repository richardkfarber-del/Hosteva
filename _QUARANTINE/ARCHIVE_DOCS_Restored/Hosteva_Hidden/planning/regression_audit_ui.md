# Hosteva UI Regression Audit Report

**Date:** April 12, 2026
**Auditor:** Black Widow (QA/Sec)
**Environment:** Production (https://hosteva.onrender.com)
**Mission:** Regression Remediation Sweep following recent UI facelift.

## Executive Summary
The recent UI facelift introduced several severe CSS class corruptions, primarily from what appears to be an overly aggressive automated find-and-replace operation. There are widespread instances of `border` being replaced with `border-none` inside larger utility classes, breaking layouts, borders, and input focus states across multiple pages. Furthermore, there are significant navigational inconsistencies between the Home, Wizard, and Dashboard modules.

## 1. Global CSS & Tailwind Class Corruptions

A botched find-and-replace operation has caused critical visual regressions across all pages, most heavily impacting the Dashboard.

*   **Broken Border Utility Classes:**
    *   **Home Page:** 
        *   The active "Home" nav link has a broken class `-b-2` instead of `border-b-2`, missing the underline.
        *   The main search input has a broken `-none` class (likely `outline-none` or `border-none`), causing focus ring anomalies.
        *   The `<footer class="... -t">` has a broken `-t` class instead of `border-t`, removing the visual separation from the main content.
    *   **Dashboard Page:** Widespread corruption of border color and opacity utilities.
        *   Sidebar border class: `border-none/80` instead of `border-white/80`.
        *   Sidebar section divider: `border-none -white/10` instead of `border-t border-white/10`.
        *   All Modal inputs (Add Property, Filter) use `focus:border-none-transparent` instead of `focus:border-transparent`.
        *   Property card dividers: `border-none -white/5` instead of `border-t border-white/5`.
*   **Inline CSS Corruptions (Home & Wizard):**
    *   In the `<style>` block for `.autocomplete-dropdown`, the properties `border-none-radius` and `border-none-bottom` are invalid. They should be `border-radius` and `border-bottom`. This results in the autocomplete dropdown having sharp corners instead of the intended rounded design, and missing dividing lines between suggestions.

## 2. Navigational and Structural Inconsistencies

*   **Disparate Navigation Shells:** The user experience is disjointed when transitioning between routes.
    *   **Home Page:** Uses a top global navigation bar.
    *   **Wizard Page:** Uses a light/white glass sidebar (`bg-white/80`) that hides on mobile. The authenticated user state is hardcoded to "John Smith" with a gradient avatar.
    *   **Dashboard Page:** Uses a dark/translucent glass sidebar (`bg-white/10`). The authenticated user state is hardcoded differently to "Host Admin" with a default Material icon.
*   **Broken/Dead Links (Orphaned Routes):**
    *   **Home Page:** "Insights" and "Support" link to `#`.
    *   **Dashboard Page:** Sidebar navigation links for "Dashboard", "My Portfolio", "Properties", "Compliance", and "Analytics" all link to `#`.
    *   **Wizard Page:** "Analytics" link points to `#`.

## 3. Component & Functional Regressions

*   **Autocomplete Dropdown Accessibility:** The autocomplete dropdown component across Home, Wizard, and Dashboard relies entirely on pointer events (mouse clicks) and lacks keyboard navigation support (Up/Down arrows, Enter key), violating basic accessibility standards.
*   **Modal Focus Trapping:** The Modals on the Dashboard (Add Property, Filters) do not trap focus, allowing users to interact with background elements while the modal is open.
*   **Dashboard Pulse Animations:** The "Active Alerts" counter and the Red "Violation" badges use harsh, unthrottled `animate-pulse` utilities which can cause visual fatigue and violate reduced-motion preferences.

## Recommended Action Plan
1.  **Immediate Reversion/Fix of CSS typos:** Run a targeted regex fix to replace `border-none-radius`, `border-none-bottom`, `border-none-transparent`, `-none`, `-b-2`, `-t`, and `-white/` back to their proper Tailwind or standard CSS equivalents.
2.  **Navigation Unification:** Consolidate the Wizard and Dashboard layouts into a single, cohesive Shell/Sidebar component.
3.  **Link Remediation:** Replace all `#` href attributes with actual routing paths or explicitly disable them visually until those features are ready.
