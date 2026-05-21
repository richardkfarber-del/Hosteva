import os
from graphbit import init, Workflow, Node

init()

def router(state):
    output = state.get("parent_output", "")
    print("Router state parent_output:", output)
    if "BACK" in output:
        return "Node A"
    return "Node C"

node_a = Node.agent("Node A", "Prompt A")
node_b = Node.condition("Router", router)
node_c = Node.agent("Node C", "Prompt C")

wf = Workflow("Test")
a_id = wf.add_node(node_a)
b_id = wf.add_node(node_b)
c_id = wf.add_node(node_c)

# Only connect a to b. B will route to A or C dynamically.
wf.connect(a_id, b_id)

try:
    wf.validate()
    print("Graph validated successfully.")
except Exception as e:
    print("Validation error:", e)
