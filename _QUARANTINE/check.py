import re, os
with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py') as f:
    content = f.read()
matches = re.findall(r'load_prompt\("([^"]+)"\)', content)
prompts_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/prompts'
for m in set(matches):
    if not os.path.exists(os.path.join(prompts_dir, m)):
        print('Missing:', m)
print('Check complete.')