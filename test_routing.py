import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node

init()

def router(state):
    output = state.get("parent_output", "")
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

wf.connect(a_id, b_id)
wf.connect(b_id, a_id)
wf.connect(b_id, c_id)

print("Graph validated:", wf.validate())
