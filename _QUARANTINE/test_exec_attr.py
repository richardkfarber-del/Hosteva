import sys
sys.path.append('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
from graphbit import Executor, LlmConfig
import inspect
print(inspect.signature(Executor.execute))
