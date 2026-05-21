from graphbit import tool, execute_tool, sync_global_tools_to_workflow

@tool("execute_shell")
def execute_shell(command: str) -> str:
    return command

sync_global_tools_to_workflow()
print(execute_tool("execute_shell", ["ls"]))
