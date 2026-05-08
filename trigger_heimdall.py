import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Node, Executor
from swarm_tools import run_shell_command

load_dotenv()
init()

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except:
        return 'You are Heimdall. Deploy the code using git push.'

local_config = LlmConfig.ollama('llama3.1-orchestrator')

heimdall_node = Node.agent(
    name='Heimdall',
    prompt='The tests have passed locally. You are authorized to deploy the code. Use your tools to run git status, git commit if needed, and git push origin master to deploy to Render.',
    system_prompt=load_prompt('heimdall_rules.md'),
    llm_config=local_config,
    tools=[run_shell_command]
)

workflow = Workflow(name='Heimdall Solo Deployment')
heimdall_id = workflow.add_node(heimdall_node)

if __name__ == '__main__':
    print("Triggering Heimdall Deployment Phase...")
    # graphbit execute doesn't take start_node_id, it executes the whole graph.
    # Since there's only one node, it will execute Heimdall.
    executor = Executor(local_config)
    result = executor.execute(workflow)
    print(result.get_node_output('Heimdall'))
