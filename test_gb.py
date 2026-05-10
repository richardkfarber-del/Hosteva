import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node

load_dotenv()
init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')

def my_router(state):
    return 'B'

node_a = Node.agent(name='A', prompt='A', llm_config=local_config)
node_b = Node.agent(name='B', prompt='B', llm_config=local_config)
router = Node.condition('Router', my_router)

wf = Workflow('Test')
ida = wf.add_node(node_a)
idb = wf.add_node(node_b)
idr = wf.add_node(router)

wf.connect(ida, idr)
wf.connect(idr, idb)

print('Compiled successfully')
