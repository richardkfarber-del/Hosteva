from graphbit import init, LlmConfig, Workflow, Executor, Node, tool, execute_workflow_tool_calls
import subprocess
import json

init()

@tool("Execute a shell command")
def execute_shell(command: str) -> str:
    """Execute a command in the shell and return its output."""
    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

config = LlmConfig.ollama('qwen2.5-coder:7b')

node = Node.agent(
    name="Test Agent",
    prompt="You must use the execute_shell tool to run 'echo hello world'. Return the exact output of the tool.",
    llm_config=config,
    tools=[execute_shell]
)

wf = Workflow("Tool_Test")
wf.add_node(node)

executor = Executor(config, timeout_seconds=3600)
state = executor.execute(wf)

outputs = state.get_all_node_outputs()
tool_calls_json = outputs.get('Test Agent', '')

print(f"Raw Output: {tool_calls_json}")

try:
    parsed = json.loads(tool_calls_json)
    if isinstance(parsed, dict):
        if "name" in parsed:
            parsed["tool_name"] = parsed.pop("name")
        if "arguments" in parsed:
            parsed["parameters"] = parsed.pop("arguments")
        tool_calls_json = json.dumps([parsed])
except Exception as e:
    pass

print("Executing tool calls...")
try:
    # Using the string name, since passing function fails
    results = execute_workflow_tool_calls(tool_calls_json, ["execute_shell"])
    print(f"Tool Results: {results}")
except Exception as e:
    print(f"Error executing tools: {e}")
