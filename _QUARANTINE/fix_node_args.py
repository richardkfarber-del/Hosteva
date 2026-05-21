import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'r') as f:
    content = f.read()

# Replace Node.agent(..., tools=io_tools) and others
# Actually, let's just do a regex replace for the Node.agent lines
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'Node.agent(' in line:
        # We need to parse it or just replace the positional args with keyword args.
        # Example: Node.agent(name='Nick Fury', prompt='Intake', system_prompt=load_prompt('nick_fury_rules.md'), llm_config=local_config)
        # We can extract the 4 parts if they match that pattern.
        m = re.search(r"Node\.agent\('([^']+)',\s*'([^']+)',\s*load_prompt\('([^']+)'\),\s*([a-z_]+_config)(?:,\s*tools=([a-z_]+))?\)", line)
        if m:
            name, prompt, prompt_file, config = m.group(1), m.group(2), m.group(3), m.group(4)
            tools = m.group(5)
            tools_str = f", tools={tools}" if tools else ""
            lines[i] = f"    {name.lower().replace('-', '_').replace(' ', '_')}_node = Node.agent(name='{name}', prompt='{prompt}', system_prompt=load_prompt('{prompt_file}'), llm_config={config}{tools_str})"

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'w') as f:
    f.write('\n'.join(lines))
