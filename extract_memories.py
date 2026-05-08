import os

source_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/agents"
dest_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agent_memories"

os.makedirs(dest_dir, exist_ok=True)

for agent_name in os.listdir(source_dir):
    agent_path = os.path.join(source_dir, agent_name)
    if os.path.isdir(agent_path):
        mem_file = os.path.join(agent_path, "MEMORY.md")
        core_file = os.path.join(agent_path, "CORE_MEMORY.md")
        
        combined_memory = f"# Personal Memory for {agent_name}\n\n"
        has_memory = False
        
        if os.path.exists(core_file):
            with open(core_file, 'r') as f:
                combined_memory += "## CORE MEMORY\n" + f.read() + "\n\n"
            has_memory = True
            
        if os.path.exists(mem_file):
            with open(mem_file, 'r') as f:
                combined_memory += "## RECENT MEMORY\n" + f.read() + "\n\n"
            has_memory = True
            
        if has_memory:
            dest_file = os.path.join(dest_dir, f"{agent_name}.md")
            with open(dest_file, 'w') as f:
                f.write(combined_memory)
            print(f"Extracted memory for {agent_name}")
