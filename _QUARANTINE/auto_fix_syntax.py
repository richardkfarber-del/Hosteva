import glob
import os
import re

# Fix run_05_development.py
file_05 = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_05_development.py'
with open(file_05, 'r') as f:
    content = f.read()

content = content.replace('raw_output = state.get_node_output(node.id)    print(raw_output)', 'raw_output = state.get_node_output(node.id)\n    print(raw_output)')
with open(file_05, 'w') as f:
    f.write(content)

# Fix run_audit_*.py
audit_files = glob.glob('/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_audit_*.py')
for file in audit_files:
    with open(file, 'r') as f:
        content = f.read()
    
    # Replace f'CRITICAL DIRECTIVE... \n\nAudit the following Phase XX artifacts:\n\n{read_artifact("...")}'
    # with f'''...'''
    content = re.sub(r"prompt=f'CRITICAL DIRECTIVE: DO NOT HALLUCINATE(.*?)\{read_artifact\((.*?)\)\}'", r"prompt=f'''CRITICAL DIRECTIVE: DO NOT HALLUCINATE\1{read_artifact(\2)}'''", content, flags=re.DOTALL)
    
    with open(file, 'w') as f:
        f.write(content)

print('Fixes applied.')
