import pytest
from src.swarm.graph import app, SwarmState

def test_full_successful_run():
    initial_state = {
        "current_phase": 1,
        "rocket_trigger_count": 0,
        "parallel_reviews": {},
    }
    
    final_state = app.invoke(initial_state)
    
    assert final_state["current_phase"] == 6 # It increments in each phase, 1->2, 2->3, 3->4, 4->5, 5->6 in shuri
    assert final_state["executive_summary"] == "All reviews compiled successfully."
    
    # Verify parallel state aggregation resolved properly
    reviews = final_state.get("parallel_reviews", {})
    assert reviews.get("black_panther") == "Approved"
    assert reviews.get("she_hulk") == "Approved"
    assert reviews.get("kang") == "Approved"
    assert reviews.get("falcon") == "Approved"

def test_rocket_failsafe_trigger():
    initial_state = {
        "current_phase": 3,
        "rocket_trigger_count": 2, # Reached threshold
        "parallel_reviews": {},
    }
    
    final_state = app.invoke(initial_state)
    
    assert "RCA: System critical failure at Phase 3" in final_state.get("rca_report", "")
    assert final_state["rocket_trigger_count"] == 2
