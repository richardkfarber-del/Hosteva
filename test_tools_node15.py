from graphbit import init, LlmConfig, Workflow, Executor, Node, tool, execute_production_tool_calls, get_tool_registry
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
    tools=["execute_shell"]
)

# The @tool decorator should have registered it, but maybe we need to pass the actual function reference to tools array?
node2 = Node.agent(
    name="Test Agent 2",
    prompt="You must use the execute_shell tool to run 'echo hello world'. Return the exact output of the tool.",
    llm_config=config,
    tools=[execute_shell]
)

print("Node 2 created.")
