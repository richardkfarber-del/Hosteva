from graphbit import init, LlmConfig, Workflow, Executor, Node, tool
import subprocess

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
print("Result text:", result.text)
print("Tool calls:", result.tool_calls)
