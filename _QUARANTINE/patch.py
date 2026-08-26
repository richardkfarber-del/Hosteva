import os

filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py"
with open(filepath, "r") as f:
    content = f.read()

# 1. Inject append_to_ledger and io_tools, plus MANDATE
append_to_ledger_code = """
def append_to_ledger(entry: str) -> str:
    \"\"\"
    Appends an entry to daily_ledger.md.
    Args:
        entry: The text to append to the ledger.
    \"\"\"
    filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md"
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry + "\\n")
        return f"SUCCESS: Appended to {filepath}"
    except Exception as e:
        return f"ERROR appending to {filepath}: {str(e)}"

io_tools = [append_to_ledger]
MANDATE = "GLOBAL MANDATE: All agents must use append_to_ledger to log their actions and decisions."
"""

if "def append_to_ledger" not in content:
    content = content.replace(
        "writer_tools = [write_file]",
        append_to_ledger_code + "\nwriter_tools = [write_file]"
    )

# Update coulson_node
old_coulson = """coulson_node = Node.agent(
    name="Agent Coulson",
    prompt="Monitor for 403 FORBIDDEN constraint violations. Log to ledger and escalate.",
    system_prompt=load_prompt("coulson_rules.md"),
    llm_config=local_config
)"""

new_coulson = """coulson_node = Node.agent(
    name="Agent Coulson",
    prompt="Monitor for 403 FORBIDDEN constraint violations. Log to ledger and escalate. AUDIT daily_ledger.md to ensure compliance.",
    system_prompt=load_prompt("coulson_rules.md") + "\\n" + MANDATE,
    llm_config=local_config,
    tools=io_tools
)"""

if "AUDIT daily_ledger.md" not in content:
    content = content.replace(old_coulson, new_coulson)

with open(filepath, "w") as f:
    f.write(content)
print("Patch applied successfully.")
