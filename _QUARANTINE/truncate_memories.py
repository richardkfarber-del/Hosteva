import os

base_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'
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
