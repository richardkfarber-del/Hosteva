import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node
from jarvis_router import get_optimal_compute

load_dotenv()
init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')


def load_system_prompt(agent_name, rules_file):
    rules = load_prompt(rules_file)
    memory_file = f"agent_memories/{agent_name.lower().replace(' ', '-')}.md"
    try:
        with open(os.path.join(os.path.dirname(__file__), memory_file), 'r') as f:
            memory = f.read()
    except FileNotFoundError:
        memory = ""
    return f"{rules}\n\n=== PAST MEMORY & EXPERTISE ===\n{memory}\n\n=== CRITICAL DIRECTIVE ===\n\nThe above is your PAST memory. You must retain the technical expertise, but DO NOT rebuild past features.\n\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below.\n\nSCOPE ADHERENCE DIRECTIVE: You must strictly adhere to the scope of the provided Sprint Backlog. Do not invent or recommend out-of-scope tasks (such as market research, SEO, or user surveys) UNLESS they are explicitly requested in the Backlog.\n"

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f'ERROR: {filename} missing.'

try:
    with open(os.path.join(os.path.dirname(__file__), '00_context_planning.md'), 'r') as f:
        memory_context = f.read()
except FileNotFoundError:
    memory_context = "ERROR: Memory context missing."

backlog_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPRINT_BACKLOG.md'
try:
    with open(backlog_path, 'r') as f:
        backlog_content = f.read()
except FileNotFoundError:
    backlog_content = "ERROR"

try:
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPIKE_FEAT-013.md', 'r') as f:
        spike_content = f.read()
except FileNotFoundError:
    spike_content = ""

full_intake_prompt = f"PROJECT MEMORY:\n{memory_context}\n\nSPIKE RESEARCH:\n{spike_content}\n\nNEW TICKET:\n{backlog_content}"

nick_fury = Node.agent(name='Nick Fury', prompt=f'Intake the following ticket:\n\n{full_intake_prompt}', system_prompt=load_system_prompt('Nick Fury', 'nick_fury_rules.md'), llm_config=get_optimal_compute('Nick Fury', 'planning'))
vision = Node.agent(name='Vision', prompt='Draft the Database and Backend Architecture Decision Record (ADR)', system_prompt=load_system_prompt('Vision', 'vision_rules.md'), llm_config=get_optimal_compute('Vision', 'planning'))
falcon = Node.agent(name='Falcon', prompt='Draft the Market and Competitor Analysis Architecture Decision Record (ADR)', system_prompt=load_system_prompt('Falcon', 'falcon_rules.md'), llm_config=get_optimal_compute('Falcon', 'planning'))
spider_man = Node.agent(name='Spider-Man', prompt='Draft the Frontend UI/UX Architecture Decision Record (ADR) based on the Spike research', system_prompt=load_system_prompt('Spider-Man', 'spider_man_rules.md'), llm_config=get_optimal_compute('Spider-Man', 'planning'))
she_hulk = Node.agent(name='She-Hulk', prompt='Draft the Legal and Compliance Architecture Decision Record (ADR) based on the Spike research', system_prompt=load_system_prompt('She-Hulk', 'she_hulk_rules.md'), llm_config=get_optimal_compute('She-Hulk', 'planning'))

workflow = Workflow('Phase1_Intake')
id_fury = workflow.add_node(nick_fury)
id_vision = workflow.add_node(vision)
id_falcon = workflow.add_node(falcon)
id_spiderman = workflow.add_node(spider_man)
id_shehulk = workflow.add_node(she_hulk)

workflow.connect(id_fury, id_vision)
workflow.connect(id_fury, id_falcon)
workflow.connect(id_fury, id_spiderman)
workflow.connect(id_fury, id_shehulk)

if __name__ == '__main__':
    print("Igniting Phase 1: Intake (Fury -> Swarm)...")
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    
    # Save the output to a physical file
    outputs = final_state.get_all_node_outputs()
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/phase1_artifact.md', 'w') as f:
        f.write("# PHASE 1 ARTIFACT\n\n")
        for agent, out in outputs.items():
            f.write(f"## {agent}\n{out}\n\n")
            
    print("Phase 1 Complete. Artifact saved to phase1_artifact.md")
    
    # Update Backlog to trigger Audit
    new_content = backlog_content.replace('**STATUS: EXECUTIVE SIGN-OFF GRANTED**', '**STATUS: PHASE 1 AUDIT**')
    with open(backlog_path, 'w') as f:
        f.write(new_content)
