import os
import sys
import re
import json
import subprocess
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node, tool, execute_tool

load_dotenv()
init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')

@tool("Execute a shell command")
def execute_shell(command: str) -> str:
    """Execute a command in the shell and return its output."""
    print(f"\n[TOOL: execute_shell] {command}")
    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

def load_golden_rules(agent_name):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'Golden Prompts Modified for Efficiency.md'), 'r') as f:
            content = f.read()
        tag_name = agent_name.upper().replace(' ', '_')
        pattern = f"<{tag_name}>(.*?)</{tag_name}>"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return f"ERROR: Rules for {agent_name} not found in Golden Prompts."
    except FileNotFoundError:
        return "ERROR: Golden Prompts file missing."

def load_system_prompt(agent_name):
    rules = load_golden_rules(agent_name)
    return f"{rules}\n\n=== CRITICAL DIRECTIVE ===\n\nYour CURRENT task is defined EXCLUSIVELY by the artifact provided below.\n\nThe project root directory is: /home/rdogen/OpenClaw_Factory/projects/Hosteva/. Write all commands using this absolute path.\n"

def parse_and_execute_tools(output_text):
    results = []
    executed_any = False
    try:
        json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', output_text, re.DOTALL)
        if not json_blocks:
            json_blocks = re.findall(r'(\{.*\"name\".*\})', output_text, re.DOTALL)
            
        blocks_to_process = []
        for block in json_blocks:
            try:
                parsed = json.loads(block)
                blocks_to_process.append(parsed)
            except json.JSONDecodeError:
                pass
                
        if not blocks_to_process:
            try:
                parsed = json.loads(output_text)
                blocks_to_process.append(parsed)
            except json.JSONDecodeError:
                pass
                
        for parsed in blocks_to_process:
            items = parsed if isinstance(parsed, list) else [parsed]
            for p in items:
                if isinstance(p, dict) and "name" in p:
                    tool_name = p["name"]
                    args = p.get("arguments", p.get("parameters", {}))
                    if args:
                        executed_any = True
                        try:
                            if tool_name in ['execute_shell', 'Execute a shell command']:
                                res = execute_shell.func(**args) if hasattr(execute_shell, 'func') else execute_shell(**args)
                            else:
                                res = f"Unknown tool: {tool_name}"
                            results.append(f"Tool {tool_name} executed:\n{res}")
                        except Exception as e:
                            results.append(f"Tool {tool_name} failed: {e}")
                
        return "\n\n".join(results) if results else "No tool executions performed.", executed_any
    except Exception as e:
        return f"Error parsing/executing tools: {e}", False

def run_single_shot(agent_name, prompt, system_prompt, tools, llm_config):
    print(f"\n--- {agent_name} Execution ---")
    safe_sys = system_prompt.replace('{', '{{').replace('}', '}}')
    safe_prompt = prompt.replace('{', '{{').replace('}', '}}')
    node = Node.agent(
        name=agent_name,
        prompt=safe_prompt,
        system_prompt=safe_sys,
        tools=tools,
        llm_config=llm_config
    )
    wf = Workflow(f"{agent_name.replace(' ', '_')}_qa")
    wf.add_node(node)
    executor = Executor(llm_config, timeout_seconds=3600)
    state = executor.execute(wf)
    outputs = state.get_all_node_outputs()
    
    text = ""
    for k, v in outputs.items():
        text = v
        break
        
    print(text)
    tool_results, executed_any = parse_and_execute_tools(text)
    if executed_any:
        print(f"\nTool Results:\n{tool_results}")
        return f"{text}\n\nTool Results:\n{tool_results}"
    return text

if __name__ == '__main__':
    print("Starting Phase 06 (QA & Deploy) with Orchestrator Pattern...")
    
    try:
        with open('05_development_state.json', 'r') as f:
            phase5_artifact = f.read()
    except FileNotFoundError:
        phase5_artifact = "ERROR: 05_development_state.json missing."

    # Spider-Man (QA)
    spider_man_sys = load_system_prompt('Spider-Man') + "\n\nCRITICAL: You must output ONLY valid JSON tool calls. Use 'arguments', NEVER 'parameters'. ONLY WRITE TO THE DIRECTORY: /home/rdogen/OpenClaw_Factory/projects/Hosteva"
    spider_man_prompt = f"Here is the code produced in the development phase:\n\n{phase5_artifact}\n\nUse execute_shell to run tests or QA checks on this code."
    sm_out = run_single_shot('Spider-Man', spider_man_prompt, spider_man_sys, [execute_shell], local_config)
    
    # Heimdall (Deploy)
    heimdall_sys = load_system_prompt('Heimdall') + "\n\nCRITICAL: You must output ONLY valid JSON tool calls. Use 'arguments', NEVER 'parameters'. ONLY WRITE TO THE DIRECTORY: /home/rdogen/OpenClaw_Factory/projects/Hosteva"
    heimdall_prompt = f"Here are the QA results from Spider-Man:\n\n{sm_out}\n\nIf the tests passed or look acceptable, use execute_shell to deploy or commit the code. NOTE: Only commit the files in app/frontend and app/backend."
    heimdall_out = run_single_shot('Heimdall', heimdall_prompt, heimdall_sys, [execute_shell], local_config)
    
    named_outputs = {
        'Spider-Man': sm_out,
        'Heimdall': heimdall_out
    }

    with open('06_qa_deploy_artifact.md', 'w') as f:
        for k, v in named_outputs.items():
            f.write(f'# {k}\n{v}\n\n')
            
    if 'kickback' in str(named_outputs).lower():
        print("KICKBACK TRIGGERED in Phase 6")
        sys.exit(3)
        
    print("Phase 06 Complete")
