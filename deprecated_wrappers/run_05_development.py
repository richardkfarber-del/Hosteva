import os
import sys
import re
import json
import subprocess
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node, tool, execute_tool, get_registered_tools

load_dotenv()
init()

primary_coder_config = LlmConfig.ollama('qwen2.5-coder:7b')

# --- Priority 3: State & Memory Isolation --- 
# Global state object to track the sprint's progress.
sprint_state = {
    "summaries": {},
    "files_modified": set(),
}

@tool("execute_shell")
def execute_shell(command: str) -> str:
    """Execute a command in the shell and return its output."""
    print(f"\n[TOOL: execute_shell] {command}")
    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

@tool("write_file")
def write_file(filepath: str, content: str) -> str:
    """Write content to a file."""
    print(f"\n[TOOL: write_file] {filepath}")
    try:
        # Track modified files for state management
        sprint_state["files_modified"].add(filepath)
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool("read_file")
def read_file(filepath: str) -> str:
    """Read content from a file."""
    print(f"\n[TOOL: read_file] {filepath}")
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def get_git_diff() -> str:
    """Get the git diff of the current workspace."""
    try:
        res = subprocess.run(["git", "diff"], capture_output=True, text=True)
        if res.returncode != 0:
            return f"Error getting git diff: {res.stderr}"
        return res.stdout if res.stdout else "No changes detected."
    except Exception as e:
        return f"Error running git diff: {str(e)}"

def load_golden_rules(agent_name):
    # ... (implementation unchanged) ...
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
    return f"""{rules}

=== CRITICAL DIRECTIVE ===

The project root directory is: /home/rdogen/OpenClaw_Factory/projects/Hosteva/. Write all files using this absolute path. Your CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below. DO NOT reference past telemetry, failed tests, or downstream artifacts.
"""

def extract_ticket(keywords):
    # ... (implementation unchanged) ...
    try:
        with open(os.path.join(os.path.dirname(__file__), '02_ticket_artifact.md'), 'r') as f:
            content = f.read()
        tickets = re.findall(r'(\**Ticket \d+:.*?)(?=\**Ticket \d+:|$)', content, re.DOTALL)
        if not tickets:
            tickets = re.split(r'(?i)\**ticket', content)
            if len(tickets) > 1:
                tickets = ['**Ticket' + t for t in tickets[1:]]

        for ticket in tickets:
            for kw in keywords:
                if kw.lower() in ticket.lower():
                    return ticket.strip()
        if tickets:
            return tickets[0].strip()
        return content # Fallback to entire artifact if format is weird
    except FileNotFoundError:
        return "ERROR: 02_ticket_artifact.md missing."

def parse_and_execute_tools(output_text):
    # ... (implementation unchanged, now uses global tools) ...
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
                            # HACK: graphbit execute_tool is broken, so we manually call the python functions
                            if tool_name in ['execute_shell', 'Execute a shell command']:
                                res = execute_shell.func(**args) if hasattr(execute_shell, 'func') else execute_shell(**args)
                            elif tool_name in ['write_file', 'Write a file']:
                                res = write_file.func(**args) if hasattr(write_file, 'func') else write_file(**args)
                            elif tool_name in ['read_file', 'Read a file']:
                                res = read_file.func(**args) if hasattr(read_file, 'func') else read_file(**args)
                            else:
                                res = f"Unknown tool: {tool_name}"
                            results.append(f"Tool {tool_name} executed:\n{res}")
                        except Exception as e:
                            results.append(f"Tool {tool_name} failed: {e}")
                
        return "\n\n".join(results) if results else "No tool executions performed.", executed_any
    except Exception as e:
        return f"Error parsing/executing tools: {e}", False

def run_agent_turn(agent_name, prompt, system_prompt, llm_config):
    print(f"\n--- {agent_name} Execution ---")
    # The graphbit workflow is now simplified to a single-shot agent turn
    node = Node.agent(name=agent_name, prompt=prompt.replace('{', '{{').replace('}', '}}'), system_prompt=system_prompt.replace('{', '{{').replace('}', '}}'), tools=[execute_shell, write_file, read_file], llm_config=llm_config)
    wf = Workflow(f"{agent_name.replace(' ', '_')}_turn")
    wf.add_node(node)
    executor = Executor(llm_config, timeout_seconds=3600)
    state = executor.execute(wf)
    raw_output = state.get_node_output(node.id())
    print(raw_output)
    
    # Execute tools based on agent output
    tool_results, _ = parse_and_execute_tools(raw_output)
    print(f"\nTool Results:\n{tool_results}")
    
    # Generate a summary of the turn for the state object
    summary_prompt = "Based on the following agent output, provide a concise, one-sentence summary of the actions taken. Focus on the result, not the process. Example: 'Created the user authentication API endpoint and wrote initial tests.'\n\nAGENT OUTPUT:\n" + str(raw_output) + "\n\nTOOL RESULTS:\n" + str(tool_results)
    summary_prompt = summary_prompt.replace('{', '[').replace('}', ']')
    summary_node = Node.agent(name="Summarizer", prompt=summary_prompt, system_prompt="You are a summarization bot.", llm_config=LlmConfig.ollama('llama3.1-orchestrator'))
    summary_wf = Workflow("Summarizer_turn")
    summary_wf.add_node(summary_node)
    summary_state = executor.execute(summary_wf)
    summary = summary_state.get_node_output(summary_node.id())
    
    sprint_state["summaries"][agent_name] = summary
    return summary

if __name__ == '__main__':
    print("Starting Phase 05 (Development) with State & Memory Isolation...")
    
    os.chdir("/home/rdogen/OpenClaw_Factory/projects/Hosteva")
    
    # 1. IRON MAN (Backend)
    im_ticket = extract_ticket(['Iron Man', 'Backend', 'API', 'Database'])
    iron_man_sys = load_system_prompt('Iron Man')
    iron_man_prompt = f"Here is your ticket:\n\n{im_ticket}\n\nBegin work on the backend. Use your tools to write files and test your code. ONLY WRITE TO THE DIRECTORY: /home/rdogen/OpenClaw_Factory/projects/Hosteva".replace('{', '{{').replace('}', '}}')
    run_agent_turn('Iron Man', iron_man_prompt, iron_man_sys, primary_coder_config)

    # 2. WASP (Frontend)
    wasp_ticket = extract_ticket(['Wasp', 'Frontend', 'UI', 'React'])
    wasp_sys = load_system_prompt('Wasp')
    code_context = get_git_diff()
    wasp_prompt = f"Here is your ticket:\n\n{wasp_ticket}\n\nIron Man has completed the backend work. Here is a summary of his changes:\n{sprint_state['summaries'].get('Iron Man', 'N/A')}\n\nHere is the current git diff of the repository, showing the exact code that was added or changed:\n\n```diff\n{code_context}\n```\n\nBuild the frontend to match the backend API. ONLY WRITE TO THE DIRECTORY: /home/rdogen/OpenClaw_Factory/projects/Hosteva".replace('{', '{{').replace('}', '}}')
    run_agent_turn('Wasp', wasp_prompt, wasp_sys, primary_coder_config)

    # 3. BLACK WIDOW (QA/Tests)
    bw_ticket = extract_ticket(['Black Widow', 'QA', 'Test', 'Spike'])
    black_widow_sys = load_system_prompt('Black Widow')
    code_context = get_git_diff()
    bw_prompt = f"Here is your ticket:\n\n{bw_ticket}\n\nThe development team has finished their work. Summaries:\n- Iron Man: {sprint_state['summaries'].get('Iron Man', 'N/A')}\n- Wasp: {sprint_state['summaries'].get('Wasp', 'N/A')}\n\nHere is the final git diff of all changes made:\n\n```diff\n{code_context}\n```\n\nWrite and execute tests to verify the implementation. ONLY WRITE TO THE DIRECTORY: /home/rdogen/OpenClaw_Factory/projects/Hosteva".replace('{', '{{').replace('}', '}}')
    run_agent_turn('Black Widow', bw_prompt, black_widow_sys, primary_coder_config)

    # Deprecate artifact.md in favor of a structured JSON state file
    with open('05_development_state.json', 'w') as f:
        # Convert set to list for JSON serialization
        sprint_state['files_modified'] = list(sprint_state['files_modified'])
        json.dump(sprint_state, f, indent=4)
            
    if 'kickback' in str(sprint_state).lower():
        print("KICKBACK TRIGGERED in Phase 5")
        sys.exit(3)
        
    print("Phase 05 Complete")
