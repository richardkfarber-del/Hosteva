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

@tool("Update Agent Memory")
def update_agent_memory(agent_name: str, sprint_learnings: str) -> str:
    """Appends new sprint learnings to an agent's memory file."""
    print(f"\n[TOOL: update_agent_memory] {agent_name}")
    filename = f"agent_memories/{agent_name.lower().replace(' ', '-')}.md"
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), 'a') as f:
            f.write(f"\n\n### Sprint Update\n{sprint_learnings}\n")
        return f"Successfully updated memory for {agent_name}"
    except Exception as e:
        return f"Failed to update memory: {str(e)}"

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
    return f"{rules}\n\n=== CRITICAL DIRECTIVE ===\n\nYour CURRENT task is defined EXCLUSIVELY by the artifacts provided below.\n"

def parse_and_execute_tools(output_text):
    results = []
    executed_any = False
    try:
        json_blocks = re.findall(r'```(?:json)?\s*(.*?)\s*```', output_text, re.DOTALL)
        if not json_blocks:
            json_blocks = re.findall(r'(\[.*?\]|\{.*?\})', output_text, re.DOTALL)
            
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
        prompt=prompt,
        system_prompt=safe_sys,
        tools=tools,
        llm_config=llm_config
    )
    wf = Workflow(f"{agent_name.replace(' ', '_')}_retro")
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
    print("Starting Phase 08 (Retrospective) with Orchestrator Pattern...")
    
    backlog = read_artifact('SPRINT_BACKLOG.md')
    shadow_ops = read_artifact('07_shadow_ops_artifact.md')
    
    context_payload = f"=== SPRINT BACKLOG ===\n{backlog}\n\n=== SPRINT ARTIFACTS ===\n{shadow_ops}"

    # Winter Soldier
    ws_sys = load_system_prompt('Winter Soldier')
    ws_prompt = f"Analyze tech debt from these sprint artifacts:\n{context_payload}"
    ws_out = run_single_shot('Winter Soldier', ws_prompt, ws_sys, [], local_config)
    
    # Rocket Raccoon
    rr_sys = load_system_prompt('Rocket Raccoon')
    rr_prompt = f"Analyze DevOps and VRAM efficiency from these sprint artifacts:\n{context_payload}"
    rr_out = run_single_shot('Rocket Raccoon', rr_prompt, rr_sys, [], local_config)
    
    # Scarlet Witch (Wanda) - Evolution Engine
    wanda_sys = load_system_prompt('Scarlet Witch') + "\n\nCRITICAL: You must output ONLY valid JSON tool calls. Use 'arguments', NEVER 'parameters'."
    wanda_prompt = f"You are the Evolution Architect. Review the sprint artifacts and use the update_agent_memory tool to permanently write new learnings to the relevant agents' memory files.\n\n{context_payload}"
    wanda_out = run_single_shot('Scarlet Witch', wanda_prompt, wanda_sys, [update_agent_memory], local_config)

    named_outputs = {
        'Winter Soldier': ws_out,
        'Rocket Raccoon': rr_out,
        'Scarlet Witch': wanda_out
    }

    with open('08_retrospective_artifact.md', 'w') as f:
        for k, v in named_outputs.items():
            f.write(f'# {k}\n{v}\n\n')
            
    print("Phase 08 Complete")
