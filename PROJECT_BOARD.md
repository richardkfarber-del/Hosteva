# Hosteva Project Board

> CURRENT_FOCUS_TARGET: BUG-001

## Active Sprint

### BUG-001: Address Eligibility Module
**Sprint Goal:** Ensure the Address Eligibility module correctly parses autocomplete selections and consistently returns accurate traffic light statuses with plain English conditions.

**Acceptance Criteria:**
```gherkin
Feature: Address Eligibility Module Bug Fix (BUG-001)

  Scenario: System resolves autocomplete selection to eligibility status
    Given the user has selected a valid address from the autocomplete dropdown
    When the backend eligibility service processes the location data
    Then the system shall return a valid traffic light status (GREEN, YELLOW, or RED)
    And the system shall return plain English regulatory conditions for the address
    And the system shall not throw an unhandled exception for unseeded addresses

  Scenario: UI displays the eligibility result correctly
    Given the backend has returned an eligibility status
    When the UI receives the payload
    Then the dashboard shall visually indicate the traffic light status
    And the dashboard shall display the plain English conditions
```
