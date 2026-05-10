import os
from graphbit import init, LlmConfig, Workflow, Executor, Node

init()
local_config = LlmConfig.ollama('llama3.1-orchestrator')

start = Node.agent(name='Nick Fury', prompt='say hi', llm_config=local_config)
iron = Node.agent(name='Iron Man', prompt='say hi', llm_config=local_config)
coulson = Node.agent(name='Agent Coulson', prompt='say hi', llm_config=local_config)
rocket = Node.agent(name='Rocket Raccoon', prompt='say hi', llm_config=local_config)
end = Node.agent(name='END', prompt='say hi', llm_config=local_config)

def c_route(state): return 'END'
c_router = Node.condition('Coulson Router', c_route)

def r_route(state): return 'END'
r_router = Node.condition('Rocket Router', r_route)

w = Workflow('test')
ids = {n.name(): w.add_node(n) for n in [start, iron, coulson, rocket, end, c_router, r_router]}

w.connect(ids['Nick Fury'], ids['Iron Man'])
w.connect(ids['Iron Man'], ids['Agent Coulson'])
w.connect(ids['Agent Coulson'], ids['Coulson Router'])
w.connect(ids['Coulson Router'], ids['Rocket Raccoon'])
w.connect(ids['Coulson Router'], ids['END'])
w.connect(ids['Rocket Raccoon'], ids['Rocket Router'])
w.connect(ids['Rocket Router'], ids['END'])

executor = Executor(local_config)
for e in executor.execute_streaming(w, stream_mode="updates"):
    if e['event'] == 'node_failed': print(e)
