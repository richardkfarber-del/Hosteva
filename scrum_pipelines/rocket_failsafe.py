import sys
from graphbit import init, LlmConfig, Workflow, Executor, Node

init()
local_config = LlmConfig.ollama('llama3.1-orchestrator')

def append_to_ledger(entry: str) -> str:
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md', 'a') as f:
        f.write(entry + '\n')
    return 'SUCCESS'

rocket = Node.agent(name='Rocket Raccoon', prompt='The pipeline crashed 3 times. Log the failure and insult the code.', system_prompt="You are Rocket.", llm_config=local_config, tools=[append_to_ledger])

workflow = Workflow(name='Rocket_Failsafe')
workflow.add_node(rocket)

try:
    executor = Executor(local_config)
    print("Rocket Raccoon Failsafe Activated. Logging catastrophic failure.")
    # executor.execute(workflow)
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
