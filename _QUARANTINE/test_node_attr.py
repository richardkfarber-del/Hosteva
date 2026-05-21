import sys
sys.path.append('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
from graphbit import Node, LlmConfig
local_config = LlmConfig.ollama('test')
n = Node.agent(name='Test Name', prompt='test', llm_config=local_config)
print(dir(n))
print(getattr(n, 'name', 'NO_NAME_ATTR'))
