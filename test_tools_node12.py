from graphbit import init, LlmConfig, Workflow, Executor, Node, tool, execute_tool
import subprocess
import json

init()

@tool("Execute a shell command")
def execute_shell(command: str) -> str:
    """Execute a command in the shell and return its output."""
    print(f"*** TOOL CALLED WITH: {command} ***")
    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

config = LlmConfig.ollama('qwen2.5-coder:7b')

node = Node.agent(
    name="Test Agent",
    prompt="Run the 'ls -la' command using your tool.",
    tools=[execute_shell],
    llm_config=config
)

workflow = Workflow("Test")
workflow.add_node(node)

executor = Executor(config)
result = executor.execute(workflow)

output = result.get_node_output("Test Agent")
print("Node output:", output)

try:
    parsed = json.loads(output)
    tool_name = parsed.get("name")
    args = parsed.get("arguments", {})
    # try passing dict instead of json string
    res = execute_tool(tool_name, args)
    print("Tool Result:", res.text)
except Exception as e:
    print("Error:", e)
