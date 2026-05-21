import os
from graphbit import init, LlmConfig, Workflow, Executor, Node

init()
local_config = LlmConfig.ollama('llama3.1-orchestrator')

def my_router(state):
    return 'A'

node_a = Node.agent(name='A', prompt='A', llm_config=local_config)
router = Node.condition('Router', my_router)

wf = Workflow('Test')
ida = wf.add_node(node_a)
idr = wf.add_node(router)

wf.connect(ida, idr)
wf.connect(idr, ida)

try:
    executor = Executor(local_config, timeout_seconds=10)
    executor.configure(allow_cycles=True)
    executor.execute(wf)
except Exception as e:
    print(f"Error: {e}")
