from graphbit import init, LlmConfig, Workflow, Executor, ExecutorConfig, Node, tool
import subprocess

init()

@tool("Execute a shell command")
def execute_shell(command: str) -> str:
    """Execute a command in the shell and return its output."""
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

exec_config = ExecutorConfig(max_steps=5)
executor = Executor(exec_config)
result = executor.execute(workflow)
print(result)
