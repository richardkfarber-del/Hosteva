with open("src/swarm/graph.py", "r") as f:
    content = f.read()

old_logic = """# Dynamic agents for Phased nodes
def phase_node(phase_name: str, agent_name: str, task: str):
    def _node(state: SwarmState):
        print(f"[{agent_name.capitalize()}] Executing {phase_name}...")
        output = run_agent(agent_name, task)
        return {"current_phase": state.get("current_phase", 1) + 1, "latest_output": output}
    return _node"""

new_logic = """import re

def parse_project_board():
    board_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md"
    try:
        with open(board_path, "r") as f:
            board_content = f.read()
    except Exception as e:
        return "Unknown Target", {}

    target_match = re.search(r"> CURRENT_FOCUS_TARGET:\\s*(.*)", board_content)
    target = target_match.group(1).strip() if target_match else "Unknown Target"

    tickets = {}
    sections = re.split(r"\\n##\\s+", board_content)
    for section in sections[1:]:
        lines = section.split('\\n')
        title_line = lines[0].strip()
        if not re.match(r"(BUG|FEAT|REGRESS)-\\d+", title_line):
            continue
        status_match = re.search(r"\\*\\*Status:\\*\\*\\s*(.*)", section)
        if not status_match:
            continue
        status = status_match.group(1).strip().lower()
        if not status.startswith("to do") and not status.startswith("in progress"):
            continue
        ac_match = re.search(r"### Acceptance Criteria:\\n(.*?)(\\n##|\\Z|\\n---)", section, re.DOTALL)
        if ac_match:
            tickets[title_line] = ac_match.group(1).strip()

    return target, tickets

# Dynamic agents for Phased nodes
def phase_node(phase_name: str, agent_name: str, task: str):
    def _node(state: SwarmState):
        print(f"[{agent_name.capitalize()}] Executing {phase_name}...")
        
        target, tickets = parse_project_board()
        
        # Inject dynamic context
        task_payload = task + "\\n\\nCURRENT_FOCUS_TARGET: " + target + "\\n\\nACTIVE TICKETS:\\n"
        for title, ac in tickets.items():
            task_payload += f"- {title}\\n{ac}\\n\\n"
            
        output = run_agent(agent_name, task_payload.strip())
        return {"current_phase": state.get("current_phase", 1) + 1, "latest_output": output}
    return _node"""

# fix double slashes from the python string definition
new_logic = new_logic.replace("\\\\n", "\\n").replace("\\\\s", "\\s").replace("\\\\d", "\\d").replace("\\\\*", "\\*").replace("\\\\Z", "\\Z")

content = content.replace(old_logic, new_logic)

with open("src/swarm/graph.py", "w") as f:
    f.write(content)

