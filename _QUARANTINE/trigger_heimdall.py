import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Node, Executor
from swarm_tools import run_shell_command, write_file

load_dotenv()
init()

api_key=os.environ.get('GOOGLE_API_KEY')
pro_config = LlmConfig.gemini(api_key, model='gemini-2.5-pro')

heimdall_node = Node.agent(
    name='Heimdall',
    prompt='''You are Heimdall, the Release Manager.
Your mission is to deploy the fix and monitor Render using its API.

1. Execute: `cd /home/rdogen/OpenClaw_Factory/projects/Hosteva && git add pyproject.toml app/main.py && git commit -m "Fix stripe dependency and syntax"`
2. Execute: `cd /home/rdogen/OpenClaw_Factory/projects/Hosteva && git push origin master:main`
3. Execute: `cd /home/rdogen/OpenClaw_Factory/projects/Hosteva && /home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python check_render.py`
4. If the output of check_render.py contains "Deployment successful!", execute write_file to create `deployment_success.txt` saying "Deployment successful, QA triggered". Otherwise, execute write_file to create `bug_ticket.txt` with the error.
''',
    llm_config=pro_config,
    tools=[run_shell_command, write_file]
)

workflow = Workflow(name='Heimdall Autonomous Deployment')
workflow.add_node(heimdall_node)

if __name__ == '__main__':
    print("Triggering Heimdall Deployment Phase...")
    executor = Executor(pro_config)
    result = executor.execute(workflow)
    print(result.get_node_output('Heimdall'))
