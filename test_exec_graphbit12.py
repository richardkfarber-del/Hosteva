from graphbit import tool, execute_tool

@tool("Execute a shell command")
def execute_shell(command: str) -> str:
    return command

print(execute_tool("Execute a shell command", ["ls"]))
