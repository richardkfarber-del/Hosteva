from graphbit import execute_tool, tool, get_registered_tools, ToolRegistry
@tool("Execute a shell command")
def execute_shell(command: str):
    return command
print("Registered:", get_registered_tools())
