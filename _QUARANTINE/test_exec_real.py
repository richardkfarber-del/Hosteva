import os
from graphbit import init, Workflow, Node, Executor, LlmConfig

init()

def router(state):
    print("ROUTER CALLED")
    return "Node C"

node_a = Node.agent("Node A", "Prompt A", llm_config=LlmConfig.ollama('llama3.1-orchestrator'))
node_b = Node.agent("Node B", "Prompt B", llm_config=LlmConfig.ollama('llama3.1-orchestrator'))
node_router = Node.condition("Router", router)
node_c = Node.agent("Node C", "Prompt C", llm_config=LlmConfig.ollama('llama3.1-orchestrator'))

wf = Workflow("Test")
a_id = wf.add_node(node_a)
b_id = wf.add_node(node_b)
router_id = wf.add_node(node_router)
c_id = wf.add_node(node_c)

wf.connect(a_id, b_id)
wf.connect(b_id, router_id)

if __name__ == '__main__':
    executor = Executor(LlmConfig.ollama('llama3.1-orchestrator'), timeout_seconds=3600)
    final_state = executor.execute(wf)
    print('Workflow executed successfully.')
