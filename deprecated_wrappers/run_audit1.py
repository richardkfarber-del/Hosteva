import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node
from jarvis_router import get_optimal_compute

load_dotenv()
init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ''

# Read the artifact
try:
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/phase1_artifact.md', 'r') as f:
        artifact_content = f.read()
        artifact_content = artifact_content.replace('{', '{{').replace('}', '}}')
except:
    artifact_content = "No artifact found."

coulson = Node.agent(name='Agent Coulson', prompt=f'Audit the following Phase 1 Artifact:\n\n{artifact_content}', system_prompt=load_prompt('agent_coulson_rules.md'), llm_config=get_optimal_compute('Agent Coulson', 'planning'))

workflow = Workflow('Phase1_Audit')
workflow.add_node(coulson)

if __name__ == '__main__':
    print("Igniting Phase 1 Audit (Coulson)...")
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    
    out = final_state.get_node_output('Agent Coulson') or ""
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/audit1_artifact.md', 'w') as f:
        f.write(f"# PHASE 1 AUDIT\n\n{out}\n")
        
    # Update Backlog based on audit result
    backlog_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPRINT_BACKLOG.md'
    with open(backlog_path, 'r') as f:
        backlog_content = f.read()
        
    if '403' in out or 'fail' in out.lower() or 'reject' in out.lower():
        new_content = backlog_content.replace('**STATUS: PHASE 1 AUDIT**', '**STATUS: HALTED - AUDIT FAILED**')
    else:
        new_content = backlog_content.replace('**STATUS: PHASE 1 AUDIT**', '**STATUS: PHASE 2 CODING**')
        
    with open(backlog_path, 'w') as f:
        f.write(new_content)
