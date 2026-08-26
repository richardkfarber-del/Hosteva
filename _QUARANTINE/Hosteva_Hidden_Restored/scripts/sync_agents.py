import json
import os

config_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/.openclaw/.openclaw/openclaw.json'
agents_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents'

print("Synchronizing Agent Markdown profiles with OpenClaw configuration...")

with open(config_path, 'r') as f:
    config = json.load(f)

if 'list' not in config.get('agents', {}):
    if 'agents' not in config:
        config['agents'] = {}
    config['agents']['list'] = []

agents_dict = {a['id']: a for a in config['agents']['list']}

for agent_name in os.listdir(agents_dir):
    agent_path = os.path.join(agents_dir, agent_name)
    if os.path.isdir(agent_path) and agent_name != "NickFury":
        soul_file = os.path.join(agent_path, "SOUL.md")
        skill_file = os.path.join(agent_path, "SKILL.md")
        style_file = os.path.join(agent_path, "STYLE.md")
        
        if os.path.exists(soul_file):
            # Combine profiles if multiple exist
            combined_prompt = ""
            with open(soul_file, 'r') as sf:
                combined_prompt += sf.read() + "\n\n"
            
            if os.path.exists(skill_file):
                with open(skill_file, 'r') as skf:
                    combined_prompt += "## SKILLS & MANDATES\n" + skf.read() + "\n\n"
                    
            if os.path.exists(style_file):
                with open(style_file, 'r') as stf:
                    combined_prompt += "## COMMUNICATION STYLE\n" + stf.read() + "\n\n"
            
            if agent_name not in agents_dict:
                agents_dict[agent_name] = {"id": agent_name}
            
            agents_dict[agent_name]["name"] = agent_name.replace("-", " ").title()
            agents_dict[agent_name]["systemPrompt"] = combined_prompt.strip()
            print(f" -> Synced {agent_name}")

config['agents']['list'] = list(agents_dict.values())

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("Synchronization complete. openclaw.json updated.")
