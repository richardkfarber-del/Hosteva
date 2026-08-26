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
        tag_name = agent_name.upper().replace(' ', '_').replace('-', '_')
        if tag_name == 'WANDA': tag_name = 'WANDA_MAXIMOFF'
        if tag_name == 'SCARLET_WITCH': tag_name = 'WANDA_MAXIMOFF'
        pattern = f"<{tag_name}>(.*?)</{tag_name}>"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return f"ERROR: Rules for {agent_name} not found in Golden Prompts."
    except FileNotFoundError:
        return "ERROR: Golden Prompts file missing."

def load_system_prompt(agent_name):
    rules = load_golden_rules(agent_name)
    return f"{rules}\n\n=== CRITICAL DIRECTIVE ===\n\nYour CURRENT task is defined EXCLUSIVELY by the artifacts provided below.\n\nThe project root directory is: /home/rdogen/OpenClaw_Factory/projects/Hosteva/. Write all commands using this absolute path.\n"

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
                            res = execute_tool(tool_name, list(args.values()))
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
    wf = Workflow(f"{agent_name.replace(' ', '_')}_ops")
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

def read_artifact(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "ERROR: Artifact missing."

if __name__ == '__main__':
    print("Starting Phase 07 (Shadow Ops) with Orchestrator Pattern...")
    
    phase1_artifact = read_artifact('phase1_artifact.md')
    sprint_backlog = read_artifact('SPRINT_BACKLOG.md')
    phase6_artifact = read_artifact('06_qa_deploy_artifact.md')
    
    context_payload = f"### PROJECT CONTEXT\n{phase1_artifact}\n\n### ACTIVE SPRINT GOAL\n{sprint_backlog}\n\n### DEPLOYED CODE & QA RESULTS\n{phase6_artifact}"

    agents = [
        ('Ultron', 'Run penetration testing and security review on the deployed feature.'),
        ('Thanos', 'Execute chaos engineering protocols and disaster recovery analysis.'),
        ('Star-Lord', 'Draft marketing, release notes, and communication materials.'),
        ('Wanda', 'Enforce system maxims, review legal/compliance implications, and rewrite reality if necessary.'),
        ('Kang', 'Optimize tooling, infrastructure, and timeline stability.'),
        ('Shuri', 'Apply background updates and suggest technological improvements.')
    ]

    named_outputs = {}
    for agent_name, directive in agents:
        sys_prompt = load_system_prompt(agent_name)
        prompt = f"{directive}\n\nBased on the following sprint context:\n\n{context_payload}"
        # Phase 7 agents primarily analyze and report, so we don't strictly require tools, but they have access to shell just in case.
        out = run_single_shot(agent_name, prompt, sys_prompt, [execute_shell], local_config)
        named_outputs[agent_name] = out

    with open('07_shadow_ops_artifact.md', 'w') as f:
        for k, v in named_outputs.items():
            f.write(f'# {k}\n{v}\n\n')
            
    print("Phase 07 Complete")
