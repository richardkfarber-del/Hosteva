import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node

# The key in the root .env is actually GEMINI_API_KEY
load_dotenv('/home/rdogen/OpenClaw_Factory/.env')
init()

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("ERROR: GEMINI_API_KEY not found.")
    exit(1)

# Pass the key to the gemini configuration
config = LlmConfig.gemini(api_key, model='gemini-2.5-pro')

def read_file(path, tail=False, lines=500):
    try:
        with open(path, 'r') as f:
            if tail:
                return "".join(f.readlines()[-lines:])
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"

agents_md = read_file('/home/rdogen/OpenClaw_Factory/projects/Hosteva/AGENTS.md')
workflow_py = read_file('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py')
loop_log = read_file('/home/rdogen/OpenClaw_Factory/projects/Hosteva/loop.log', tail=True, lines=200)
swarm_log = read_file('/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_loop.log', tail=True, lines=200)
strike_report = read_file('/home/rdogen/OpenClaw_Factory/projects/Hosteva/strike_team_report.md', tail=True, lines=200)

context = f"""
=== SYSTEM ARCHITECTURE (workflow.py snippet) ===
{workflow_py[:3000]}

=== RECENT ERROR LOGS (swarm_loop.log snippet) ===
{swarm_log}

=== RECENT EXECUTION LOGS (loop.log snippet) ===
{loop_log}

=== COULSON STRIKE REPORT (snippet) ===
{strike_report}
"""

prompt = f"Analyze the following system context, logs, and architecture. Identify the root causes of our 3-strike kickbacks, ghost state caching, and GraphBit pipeline failures. Provide your recommended fixes from your unique perspective.\n\n{context}"

wf = Workflow('Infra_Spike')

for agent in ['Rocket Raccoon', 'Iron Man', 'Phil Coulson', 'Falcon']:
    sys_prompt = f"You are {agent}. Here is the complete agent roster and your personality profile:\n{agents_md}\n\nAct strictly in character. You are reviewing our internal infrastructure, architecture, graphbit configuration, memory configuration, and error logs over the past week. Identify the root cause(s) and recommended fixes for the multitude of issues we've been experiencing (specifically the ghost state caching, 3-strike kickbacks, and deprecated GraphBit methods)."
    
    n = Node.agent(
        name=agent,
        prompt=prompt,
        system_prompt=sys_prompt,
        llm_config=config
    )
    wf.add_node(n)

print("Executing Infra Spike Workflow...")
executor = Executor(config, timeout_seconds=3600)
try:
    state = executor.execute(wf)
    outputs = state.get_all_node_outputs()
    
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/infra_spike_results.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f"# {k}\n\n{v}\n\n---\n\n")
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
