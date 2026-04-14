import re

with open("src/swarm/graph.py", "r") as f:
    content = f.read()

# 1. Add qa_gate_status to SwarmState
content = content.replace(
    "    error_detected: bool\n    dreamstate_lock: bool",
    "    error_detected: bool\n    qa_gate_status: Optional[str]\n    dreamstate_lock: bool"
)

# 2. Add bug_ticket_generator node
new_node = """
def node_bug_ticket_generator(state: SwarmState):
    print("[Hawkeye] QA Gate FAILED. Generating BUG ticket...")
    return {
        "rocket_trigger_count": state.get("rocket_trigger_count", 0) + 1,
        "qa_gate_status": None,
        "current_phase": 1
    }

# Placeholder generic agents
"""
content = content.replace("# Placeholder generic agents\n", new_node)

# 3. Update coulson_router
router_old = """def coulson_router(state: SwarmState) -> str:
    # Global Law #3: Rocket Failsafe
    if state.get("rocket_trigger_count", 0) >= 2:
        return "rocket"
    
    phase = state.get("current_phase", 1)"""
    
router_new = """def coulson_router(state: SwarmState) -> str:
    # Global Law #3: Rocket Failsafe
    if state.get("rocket_trigger_count", 0) >= 2:
        return "rocket"
        
    if state.get("qa_gate_status") == "FAIL":
        return "bug_ticket_generator"
    
    phase = state.get("current_phase", 1)"""
    
content = content.replace(router_old, router_new)

# 4. Add node and edges
node_add = """workflow.add_node("coulson", node_coulson)
workflow.add_node("bug_ticket_generator", node_bug_ticket_generator)"""
content = content.replace('workflow.add_node("coulson", node_coulson)', node_add)

edge_add = """        "rocket": "rocket",
        "bug_ticket_generator": "bug_ticket_generator","""
content = content.replace('        "rocket": "rocket",', edge_add)

edge2_add = """workflow.add_edge("bug_ticket_generator", "coulson")

# Rocket Failsafe Path"""
content = content.replace('# Rocket Failsafe Path', edge2_add)

with open("src/swarm/graph.py", "w") as f:
    f.write(content)
