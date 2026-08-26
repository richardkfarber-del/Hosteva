from graphbit import tool, execute_tool

@tool("execute_shell")
def execute_shell(command: str) -> str:
    return command

print(execute_tool("execute_shell", {"command": "ls"}))
