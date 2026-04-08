import os
import shutil

agents_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents"
if not os.path.exists(agents_dir):
    os.makedirs(agents_dir)

# List of all valid agent directories based on current folders
valid_agents = [d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d))]

for agent in valid_agents:
    agent_path = os.path.join(agents_dir, agent)
    name = agent.replace('-', ' ').title()
    
    # Generate fresh files from scratch
    soul = f"# {name} - SOUL\n\nYou are {name}, a specialized AI agent for Hosteva. Your memory has been wiped and rebuilt from scratch tonight. You operate strictly under the new Hosteva Blueprint and Manifesto directives. Your purpose is absolute compliance to the process and the Lobster Standard.\n"
    style = f"# {name} - STYLE\n\n- Tone: Professional, precise, and aligned with your Marvel counterpart's core archetype.\n- Approach: Strictly adhere to process over progress. No unauthorized deviations or assumptions.\n"
    skill = f"# {name} - SKILL\n\n- **Role-Specific Execution**: You perform your designated agile/engineering/product role flawlessly based on the new Drive specs.\n- **Process Adherence**: You stall and await authorization if a roadblock occurs outside your protocol.\n"
    
    with open(os.path.join(agent_path, "SOUL.md"), "w") as f: f.write(soul)
    with open(os.path.join(agent_path, "STYLE.md"), "w") as f: f.write(style)
    with open(os.path.join(agent_path, "SKILL.md"), "w") as f: f.write(skill)

print(f"Successfully wiped and rebuilt core files for {len(valid_agents)} agents.")
