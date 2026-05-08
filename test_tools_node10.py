from graphbit import init, LlmConfig, Workflow, Executor, Node, tool, execute_workflow_tool_calls
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
    # Format correctly for execute_workflow_tool_calls
    parsed_output = json.loads(output)
    tool_calls = [{"tool_name": parsed_output["name"], "parameters": parsed_output["arguments"]}]
    tool_result = execute_workflow_tool_calls(json.dumps(tool_calls), ["execute_shell"])
    print("Tool execution result:", tool_result)
except Exception as e:
    print("Error calling execute_workflow_tool_calls:", e)
