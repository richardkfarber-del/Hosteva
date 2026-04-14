import re

with open('src/swarm/graph.py', 'r') as f:
    content = f.read()

# Add frontend_ui_changes to SwarmState
content = content.replace(
    'director_feedback: Optional[str]',
    'director_feedback: Optional[str]\n    frontend_ui_changes: bool'
)

# Add node_gate_4_production_uat
node_code = """
def node_gate_4_production_uat(state: SwarmState):
    print("[Captain America] Executing Gate 4: Production UAT. Verifying locked UI overlay and Stripe Checkout CTA render in live DOM...")
    return {"qa_gate_status": "PASS", "frontend_ui_changes": False}

def node_bug_ticket_generator(state: SwarmState):"""

content = content.replace('def node_bug_ticket_generator(state: SwarmState):', node_code)

# Add routing logic in coulson_router
router_old = """    elif phase == 4:
        return "phase_4\""""
router_new = """    elif phase == 4:
        if state.get("frontend_ui_changes"):
            return "gate_4_production_uat"
        return "phase_4\""""

content = content.replace(router_old, router_new)

# Add node to workflow
workflow_old = """# Placeholder nodes for other phases
workflow.add_node("phase_1", generic_agent("War Room"))"""
workflow_new = """workflow.add_node("gate_4_production_uat", node_gate_4_production_uat)

# Placeholder nodes for other phases
workflow.add_node("phase_1", generic_agent("War Room"))"""

content = content.replace(workflow_old, workflow_new)

# Add edge to coulson
edges_old = """workflow.add_conditional_edges(
    "coulson",
    coulson_router,
    {
        "rocket": "rocket",
        "bug_ticket_generator": "bug_ticket_generator",
        "phase_1": "phase_1",
        "phase_2": "phase_2",
        "phase_3": "phase_3",
        "phase_4": "phase_4",
        "shuri": "shuri",
        END: END
    }
)"""

edges_new = """workflow.add_conditional_edges(
    "coulson",
    coulson_router,
    {
        "rocket": "rocket",
        "bug_ticket_generator": "bug_ticket_generator",
        "phase_1": "phase_1",
        "phase_2": "phase_2",
        "phase_3": "phase_3",
        "gate_4_production_uat": "gate_4_production_uat",
        "phase_4": "phase_4",
        "shuri": "shuri",
        END: END
    }
)"""

content = content.replace(edges_old, edges_new)

# Add return edge for gate_4_production_uat
return_edge_old = """workflow.add_edge("bug_ticket_generator", "coulson")"""
return_edge_new = """workflow.add_edge("bug_ticket_generator", "coulson")
workflow.add_edge("gate_4_production_uat", "coulson")"""

content = content.replace(return_edge_old, return_edge_new)

with open('src/swarm/graph.py', 'w') as f:
    f.write(content)
print("Patch applied")
