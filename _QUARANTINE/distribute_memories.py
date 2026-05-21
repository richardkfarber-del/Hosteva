import os
import shutil

agents_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents"
base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"

# Map agents to their specific contexts
mapping = {
    "spider-man": "00_context_frontend.md",
    "iron-man": "00_context_backend.md",
    "scarlet-witch": "00_context_compliance.md",
    "star-lord": "00_context_marketing.md",
    "captain-america": "00_context_planning.md",
    "nick-fury": "00_context_planning.md",
    "jarvis": "00_context_backend.md"
}

# Load a fallback/general context
with open(f"{base_dir}/00_context_planning.md", "r") as f:
    general_context = f.read()

for agent in os.listdir(agents_dir):
    agent_path = os.path.join(agents_dir, agent)
    if os.path.isdir(agent_path):
        mem_file = os.path.join(agent_path, "CORE_MEMORY.md")
        context_file = mapping.get(agent)
        
        if context_file and os.path.exists(os.path.join(base_dir, context_file)):
            with open(os.path.join(base_dir, context_file), "r") as cf:
                content = cf.read()
        else:
            content = general_context
            
        with open(mem_file, "w") as mf:
            mf.write(content)
        print(f"Updated CORE_MEMORY.md for {agent}")
