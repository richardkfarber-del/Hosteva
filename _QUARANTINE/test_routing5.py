import os
from graphbit import init, Workflow, Node

init()

def router(state):
    output = state.get("node_outputs", {}).get("Node B", "")
    print("Router state node_outputs:", state.get("node_outputs", {}))
    if "BACK" in output:
        return "Node A"
    return "Node C"

node_a = Node.agent("Node A", "Prompt A")
node_b = Node.agent("Node B", "Prompt B")
node_router = Node.condition("Router", router)
node_c = Node.agent("Node C", "Prompt C")

wf = Workflow("Test")
a_id = wf.add_node(node_a)
b_id = wf.add_node(node_b)
router_id = wf.add_node(node_router)
c_id = wf.add_node(node_c)

wf.connect(a_id, b_id)
wf.connect(b_id, router_id)

try:
    wf.validate()
    print("Graph validated successfully.")
except Exception as e:
    print("Validation error:", e)
