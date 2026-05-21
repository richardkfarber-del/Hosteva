import os

base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents"
for d in os.listdir(base_dir):
    agent_dir = os.path.join(base_dir, d)
    if os.path.isdir(agent_dir):
        core_mem_path = os.path.join(agent_dir, "CORE_MEMORY.md")
        agent_id = d
        identity_path = os.path.join(agent_dir, "IDENTITY.md")
        if os.path.exists(identity_path):
            try:
                with open(identity_path, "r") as f:
                    for line in f:
                        if "Agent ID:" in line:
                            agent_id = line.split("Agent ID:")[1].strip()
                            break
            except Exception:
                pass
        
        try:
            with open(core_mem_path, "w") as f:
                f.write(f"# CORE MEMORY: {agent_id}\n\n")
                f.write("This is a minimal fallback memory file. Standard memory operations are temporarily offline due to database connection failures.\n")
                f.write("Core constraints and identity directives remain active.\n")
        except PermissionError:
            print(f"Skipped {d} due to permissions.")

