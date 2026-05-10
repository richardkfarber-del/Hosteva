import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node

# Load environment variables from the project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')

def run_single_agent(phase_name, agent_name, skill_file, config, initial_state):
    skill_content = f"Missing skill file: {skill_file}"
    skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills", skill_file)
    if os.path.exists(skill_path):
        with open(skill_path, "r") as f:
            skill_content = f.read()
            
    prompt = f"Execute your skill based on the following context. Do not ask for more information, just output the required artifacts.\n\nContext:\n{initial_state.get('input', '')}"
    system_prompt = f"You are {agent_name}. Follow this skill taxonomy strictly:\n\n{skill_content}"
    
    workflow = Workflow(name=phase_name)
    agent_node = Node.agent(name=agent_name.replace(' ', '_'), prompt=prompt, system_prompt=system_prompt, llm_config=config)
    workflow.add_node(agent_node)
    
    executor = Executor(config, timeout_seconds=3600)
    result = executor.execute(workflow)
    if hasattr(result, 'get_all_node_outputs'): return result.get_all_node_outputs()
    return str(result)
