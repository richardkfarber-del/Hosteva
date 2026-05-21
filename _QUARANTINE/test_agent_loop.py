import os
import re
import json
import subprocess
from graphbit import init, LlmConfig, Workflow, Executor, Node, tool, execute_tool

init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')
coder_config = LlmConfig.ollama('qwen2.5-coder:7b')

@tool("Execute a shell command")
def execute_shell(command: str) -> str:
    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

@tool("Write a file")
def write_file(filepath: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool("Read a file")
def read_file(filepath: str) -> str:
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def parse_and_execute_tools_with_results(output_text):
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
                            results.append(f"Tool {tool_name} executed successfully:\n{res}")
                        except Exception as e:
                            results.append(f"Tool {tool_name} failed: {e}")
                
        return "\n\n".join(results) if results else "No tool executions performed.", executed_any
    except Exception as e:
        return f"Error parsing/executing tools: {e}", False

def run_agent_loop(agent_name, initial_prompt, system_prompt, tools, llm_config, max_turns=3):
    current_prompt = initial_prompt
    final_output = ""
    
    for turn in range(max_turns):
        print(f"\n--- {agent_name} Turn {turn+1} ---")
        node = Node.agent(
            name=agent_name,
            prompt=current_prompt,
            system_prompt=system_prompt,
            tools=tools,
            llm_config=llm_config
        )
        wf = Workflow(f"{agent_name}_turn_{turn}")
        wf.add_node(node)
        executor = Executor(llm_config, timeout_seconds=3600)
        state = executor.execute(wf)
        outputs = state.get_all_node_outputs()
        text = outputs.get(agent_name, "")
        
        final_output += f"\n\n### Turn {turn+1}:\n{text}"
        print(text)
        
        tool_results, executed_any = parse_and_execute_tools_with_results(text)
        if not executed_any:
            print("No tools executed. Ending loop.")
            break
            
        print(f"\nTool Results:\n{tool_results}")
        final_output += f"\n\n### Tool Results:\n{tool_results}"
        current_prompt = f"{current_prompt}\n\nAssistant: {text}\n\nTool Results:\n{tool_results}\n\nContinue your task."
        
    return final_output

if __name__ == '__main__':
    sys_prompt = "You are a test agent. You must use tools. Output ONLY valid JSON for tool calls: {\"name\": \"read_file\", \"arguments\": {\"filepath\": \"test.txt\"}}"
    run_agent_loop('TestAgent', 'Read 02_ticket_artifact.md and tell me what is inside.', sys_prompt, [read_file], coder_config)
