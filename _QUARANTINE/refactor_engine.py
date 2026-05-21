import os
import re

base_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'

def patch_file(filename, replacements):
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'r') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

# 1. Fix run_02_ticket_creation.py
patch_file('run_02_ticket_creation.py', [
    ("system_prompt=load_prompt('hawkeye_rules.md')", "system_prompt=load_system_prompt('Hawkeye', 'hawkeye_rules.md')")
])

# 2. Fix run_05_development.py
with open(os.path.join(base_dir, 'run_05_development.py'), 'r') as f:
    dev_content = f.read()

# Replace system_prompts
dev_content = dev_content.replace("system_prompt=load_prompt('black_widow_rules.md')", "system_prompt=load_system_prompt('Black Widow', 'black_widow_rules.md')")
dev_content = dev_content.replace("system_prompt=load_prompt('iron_man_rules.md')", "system_prompt=load_system_prompt('Iron Man', 'iron_man_rules.md')")
dev_content = dev_content.replace("system_prompt=load_prompt('wasp_rules.md')", "system_prompt=load_system_prompt('Wasp', 'wasp_rules.md')")

# Replace tool parser
old_parser = re.search(r'def parse_and_execute_tools.*?return f"Error parsing/executing tools: \{e\}"', dev_content, re.DOTALL)
if old_parser:
    new_parser = '''def parse_and_execute_tools(output_text):
    results = []
    import json
    import re
    try:
        json_blocks = re.findall(r'```(?:json)?\\s*(.*?)\\s*```', output_text, re.DOTALL)
        if not json_blocks:
            json_blocks = re.findall(r'(\\[.*?\\]|\\{.*?\\})', output_text, re.DOTALL)
            
        blocks_to_process = []
        for block in json_blocks:
            try:
                parsed = json.loads(block)
                blocks_to_process.append(parsed)
            except json.JSONDecodeError:
                pass
                
        if not blocks_to_process:
            try:
                parsed = json.loads(output_text)
                blocks_to_process.append(parsed)
            except json.JSONDecodeError:
                pass
                
        for parsed in blocks_to_process:
            items = parsed if isinstance(parsed, list) else [parsed]
            for p in items:
                if isinstance(p, dict) and "name" in p:
                    tool_name = p["name"]
                    args = p.get("arguments", p.get("parameters", {}))
                    if args:
                        try:
                            res = execute_tool(tool_name, list(args.values()))
                            results.append(f"Tool {tool_name} executed:\\n{res}")
                        except Exception as e:
                            results.append(f"Tool {tool_name} failed: {e}")
                
        return "\\n\\n".join(results) if results else "No tool executions performed."
    except Exception as e:
        return f"Error parsing/executing tools: {e}"'''
    dev_content = dev_content.replace(old_parser.group(0), new_parser)

# Replace UUID output handling
old_output_handling = """    outputs = final_state.get_all_node_outputs()
    
    # Execute tools
    for agent_name, text in outputs.items():
        print(f"\nProcessing tools for {agent_name}...")
        tool_results = parse_and_execute_tools(text)
        outputs[agent_name] += f"\n\n### Tool Execution Results\n```\n{tool_results}\n```"

    with open('05_development_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {k}\n{v}\n\n')"""

new_output_handling = """    outputs = final_state.get_all_node_outputs()
    
    named_outputs = {}
    for node in nodes:
        node_id = ids[node.name()]
        if node_id in outputs:
            named_outputs[node.name()] = outputs[node_id]
        elif node.name() in outputs:
            named_outputs[node.name()] = outputs[node.name()]
            
    # Execute tools
    for agent_name, text in named_outputs.items():
        print(f"\nProcessing tools for {agent_name}...")
        tool_results = parse_and_execute_tools(text)
        named_outputs[agent_name] += f"\n\n### Tool Execution Results\n```\n{tool_results}\n```"

    with open('05_development_artifact.md', 'w') as f:
        for k, v in named_outputs.items():
            f.write(f'# {k}\n{v}\n\n')"""

dev_content = dev_content.replace(old_output_handling, new_output_handling)

with open(os.path.join(base_dir, 'run_05_development.py'), 'w') as f:
    f.write(dev_content)

# 3. Fix run_08_retrospective.py UUIDs
with open(os.path.join(base_dir, 'run_08_retrospective.py'), 'r') as f:
    retro_content = f.read()

old_retro_output = """    outputs = final_state.get_all_node_outputs()
    with open('08_retrospective_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {k}\n{v}\n\n')"""

new_retro_output = """    outputs = final_state.get_all_node_outputs()
    named_outputs = {}
    for node in nodes:
        node_id = ids[node.name()]
        if node_id in outputs:
            named_outputs[node.name()] = outputs[node_id]
        elif node.name() in outputs:
            named_outputs[node.name()] = outputs[node.name()]
            
    with open('08_retrospective_artifact.md', 'w') as f:
        for k, v in named_outputs.items():
            f.write(f'# {k}\n{v}\n\n')"""

retro_content = retro_content.replace(old_retro_output, new_retro_output)
with open(os.path.join(base_dir, 'run_08_retrospective.py'), 'w') as f:
    f.write(retro_content)
    
# 4. Truncate memories
memories_dir = os.path.join(base_dir, 'agent_memories')
if os.path.exists(memories_dir):
    for filename in os.listdir(memories_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(memories_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            lines = content.split('\n')
            if len(lines) > 50:
                truncated = '\n'.join(lines[:50]) + "\n\n[MEMORY TRUNCATED TO PREVENT CONTEXT COLLAPSE]"
                with open(filepath, 'w') as f:
                    f.write(truncated)

print("Refactor complete.")
