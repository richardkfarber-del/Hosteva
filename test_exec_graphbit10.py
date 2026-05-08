from graphbit import tool, execute_tool, ToolRegistry
registry = ToolRegistry()

@registry.register("execute_shell")
def execute_shell(command: str) -> str:
    return command

print(registry.execute("execute_shell", ["ls"]))
