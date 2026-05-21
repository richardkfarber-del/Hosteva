from graphbit import execute_tool, tool, get_registered_tools
@tool("Execute a shell command")
def execute_shell(command: str):
    return command
print(get_registered_tools())
