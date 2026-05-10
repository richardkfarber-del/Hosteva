import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node
from swarm_tools import run_shell_command, read_file, write_file

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
    system_prompt = f"You are {agent_name}. Follow this skill taxonomy strictly:\n\n{skill_content}\n\nCRITICAL INSTRUCTION: You are authorized and required to use tools. Use run_shell_command to execute terminal commands (like git or testing). Use read_file to read code. Use write_file to actually create or modify files. DO NOT output fake code blocks claiming you fixed a file. YOU MUST USE THE WRITE_FILE TOOL to physically change the code on the hard drive. THE PROJECT ROOT IS /home/rdogen/OpenClaw_Factory/projects/Hosteva. ALL FILE PATHS MUST BE ABSOLUTE PATHS STARTING WITH THIS DIRECTORY. DO NOT TRY TO EDIT /Dockerfile."
    
    workflow = Workflow(name=phase_name)
    agent_node = Node.agent(name=agent_name.replace(' ', '_'), prompt=prompt, system_prompt=system_prompt, llm_config=config, tools=[run_shell_command, read_file, write_file])
    workflow.add_node(agent_node)
    
    executor = Executor(config, timeout_seconds=3600)
    result = executor.execute(workflow)
    if hasattr(result, 'get_all_node_outputs'): return result.get_all_node_outputs()
    return str(result)
