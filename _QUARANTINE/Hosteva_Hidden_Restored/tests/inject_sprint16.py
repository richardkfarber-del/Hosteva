import redis
import json

r = redis.Redis.from_url("redis://localhost:6379/0")

# Task 5: Wasp UI Integration
task_desc = """
TICKET-05: FEAT-016 Dashboard UI Integration
Assignee: Wasp (Frontend)
Story: As a user, I want my dashboard to display my subscription tier, remaining quota, and query history list so that I can track my account usage.
Acceptance Criteria:
Feature: Dashboard Display
  Scenario: Display Dashboard Information
    Given a user is logged into the application and navigating to the dashboard
    When the "dashboard.html" page loads
    Then the frontend client fetches data from "/api/v1/dashboard/overview"
    And the UI displays the subscription tier, remaining quota, and query history list based on the JSON payload.
"""

r.rpush("swarm:queue:tasks", json.dumps({
    "ticket_id": "TICKET-05", 
    "status": "PENDING", 
    "task": task_desc, 
    "retry_count": 0
}))

print("Injected TICKET-05 into Redis DB 0.")