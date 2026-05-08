import os
import glob
import re

files = glob.glob('/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_*.py')

for file in files:
    with open(file, 'r') as f:
        content = f.read()
        
    # Skip if already patched
    if 'from jarvis_router import get_optimal_compute' in content:
        continue
        
    # Inject router import
    content = content.replace('from graphbit import init, LlmConfig, Workflow, Executor, Node', 'from graphbit import init, LlmConfig, Workflow, Executor, Node\nfrom jarvis_router import get_optimal_compute')
    
    # Match Node.agent(name='AgentName', ..., llm_config=something)
    pattern = r"Node\.agent\(\s*name\s*=\s*['\"]([^'\"]+)['\"].*?llm_config\s*=\s*[^,\)]+"
    
    def replacer(match):
        agent_name = match.group(1)
        # Determine task category based on file name or simple heuristic
        if '04_environment' in file or '05_development' in file or '06_qa' in file:
            task = 'coding'
        else:
            task = 'planning'
            
        full_match = match.group(0)
        # Replace the llm_config part
        new_string = re.sub(r'llm_config\s*=\s*[^,\)]+', f"llm_config=get_optimal_compute('{agent_name}', '{task}')", full_match)
        return new_string

    new_content = re.sub(pattern, replacer, content)
    
    with open(file, 'w') as f:
        f.write(new_content)

print("Patch complete.")
