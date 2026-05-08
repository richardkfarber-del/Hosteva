import os
import glob

files = glob.glob('/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_*.py')

for file in files:
    with open(file, 'r') as f:
        content = f.read()
    
    content = content.replace('state.node_outputs.get', 'state.get_node_output')
    content = content.replace('final_state.node_outputs.get', 'final_state.get_node_output')
    content = content.replace('outputs = state.node_outputs', 'outputs = state.get_all_node_outputs()')
    content = content.replace('outputs = final_state.node_outputs', 'outputs = final_state.get_all_node_outputs()')
    content = content.replace('out_dict = final_state.node_outputs', 'out_dict = final_state.get_all_node_outputs()')
    content = content.replace('outputs = res.node_outputs', 'outputs = res.get_all_node_outputs()')
    
    with open(file, 'w') as f:
        f.write(content)

print('Patched all files.')
