import os
from graphbit import init, LlmConfig, Workflow, Executor, Node

init()
local_config = LlmConfig.ollama('llama3.1-orchestrator')

start = Node.agent(name='Start', prompt='say hi', llm_config=local_config)
def route(state):
    return 'END_NODE'
router = Node.condition('Router', route)
end = Node.agent(name='END_NODE', prompt='say bye', llm_config=local_config)

w = Workflow('test')
start_id = w.add_node(start)
router_id = w.add_node(router)
end_id = w.add_node(end)

w.connect(start_id, router_id)
w.connect(router_id, end_id)

executor = Executor(local_config)
for e in executor.execute_streaming(w, stream_mode="updates"):
    print(e)
