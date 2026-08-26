from graphbit import execute_tool, tool
@tool("test")
def my_tool(command: str):
    return command
print(execute_tool("test", ["ls"]))
