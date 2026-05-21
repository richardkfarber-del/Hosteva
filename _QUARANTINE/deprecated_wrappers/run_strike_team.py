import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Executor, Node, Workflow

load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
if 'GOOGLE_API_KEY' in os.environ and 'GEMINI_API_KEY' not in os.environ:
    os.environ['GEMINI_API_KEY'] = os.environ['GOOGLE_API_KEY']

init()

base_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'
agents_dir = os.path.join(base_dir, 'agents')

def load_agent_context(agent_name):
    context = []
    agent_path = os.path.join(agents_dir, agent_name)
    files_to_load = ['IDENTITY.md', 'SOUL.md', 'STYLE.md', 'SKILL.md', 'CORE_MEMORY.md', 'TOOLS.md']
    for f in files_to_load:
        filepath = os.path.join(agent_path, f)
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                context.append(f"--- {f} ---\n{file.read()}\n")
    return "\n".join(context)

def read_file_safe(filepath, tail_chars=4000):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return content[-tail_chars:] if len(content) > tail_chars else content
    except Exception as e:
        return str(e)

ledger_content = read_file_safe(os.path.join(base_dir, 'daily_ledger.md'))
loop_content = read_file_safe(os.path.join(base_dir, 'loop.log'))
workflow_content = read_file_safe(os.path.join(base_dir, 'PHASED_WORKFLOW_PLAN.md'), tail_chars=8000)

mission_prompt = f"""
STRIKE TEAM MISSION:
The Swarm has halted due to a 3-strike kickback limit. You are tasked with reviewing our roster, reviewing our workflow, reviewing our tooling, and searching the web (or applying your advanced knowledge) to figure out what we are doing wrong and what we need to do to resolve all of our issues.

=== LOOP LOG (LATEST) ===
{loop_content}

=== DAILY LEDGER (LATEST) ===
{ledger_content}

=== WORKFLOW PLAN ===
{workflow_content}
"""

# Upgrading to Gemini Pro API
llm_config = LlmConfig.gemini(api_key=os.environ.get('GOOGLE_API_KEY'), model='gemini-3.1-pro-preview')

team = ['iron-man', 'captain-america', 'vision', 'black-widow']
nodes = []

for member in team:
    sys_prompt = load_agent_context(member)
    node = Node.agent(
        name=member.replace('-', ' ').title(),
        prompt=mission_prompt,
        system_prompt=sys_prompt,
        llm_config=llm_config
    )
    nodes.append(node)

wf = Workflow('Strike_Team_Investigation')
for node in nodes:
    wf.add_node(node)

executor = Executor(llm_config, timeout_seconds=3600)
print("Assembling Strike Team: " + ", ".join(team))
print("Upgrading to Gemini Pro API...")
print("Executing Strike Team Workflow...")

try:
    res = executor.execute(wf)
    out = "\nSTRIKE TEAM OUTPUT:\n\n"
    outputs = res.get_all_node_outputs()
    for node_id, output in outputs.items():
        out += f"========================================\n[AGENT: {node_id}]\n{output}\n\n"
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/strike_team_report.md', 'w') as f:
        f.write(out)
    print("Strike team execution complete. Report saved to strike_team_report.md")
except Exception as e:
    error_msg = f"\nERROR EXECUTING WORKFLOW: {e}"
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/strike_team_report.md', 'w') as f:
        f.write(error_msg)
    print(error_msg)
