# BUG-007: Compliance UI XSS Vulnerability & Test Fixtures
**Domain:** Engineering / Security
**Status:** **READY FOR EXECUTION**

## Description
During Sprint 8 QA Gate, a Cross-Site Scripting (XSS) vulnerability was identified in the Compliance UI. `marked.js` output is being directly rendered via `innerHTML` without sanitization, posing a critical security risk. Additionally, `pytest-mock` is missing or misconfigured in the test environment, causing `tests/test_compliance_ui.py` to fail.

## Requirements
1. **Iron Man (Lead Backend & Security):** 
   - Implement a sanitization library (e.g., `DOMPurify`) in the frontend logic.
   - Ensure all `marked.js` markdown output is strictly sanitized before being injected into the DOM via `innerHTML`.
2. **Iron Man (Test Infrastructure):**
   - Fix the `pytest-mock` dependency issue affecting `tests/test_compliance_ui.py` to ensure local tests pass.
3. **Captain America (QA Gatekeeper):**
   - Re-verify the UI tests after the implementation and ensure the fix prevents script injection payloads.

## Swarm Review (Sign-offs)
- [x] **Vision:** Approved. No database schema changes required.
- [x] **Iron Man:** Approved. Will integrate `DOMPurify` and fix the `pytest-mock` dependency in the test suite.
- [x] **Black Widow:** Approved. Confirmed XSS vector via `innerHTML` and verified `DOMPurify` is the correct mitigation.
- [x] **Captain America:** Approved. Test fixtures need `pytest-mock` to mock the async requests properly.
