import os

def patch_file(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Replace load_prompt with load_system_prompt in Node.agent calls if not already done
        if 'load_system_prompt(' not in content and 'load_prompt(' in content:
            content = content.replace('system_prompt=load_prompt(', 'system_prompt=load_system_prompt(')
            
            # Ensure load_system_prompt is defined
            if 'def load_system_prompt' not in content:
                directive = """

def load_system_prompt(agent_name, rules_file):
    rules = load_prompt(rules_file)
    return f"{rules}\\n\\n=== CRITICAL DIRECTIVE ===\\n\\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below. DO NOT reference past telemetry, failed tests, or downstream artifacts.\\n"
"""
                content = content.replace('def load_prompt(', directive + 'def load_prompt(')
                
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Patched {filepath}")
    except Exception as e:
        print(f"Error patching {filepath}: {e}")

files = [
    'run_05_development.py',
    'run_06_qa_deploy.py',
    'run_07_shadow_ops.py',
    'run_08_retrospective.py'
]

for file in files:
    patch_file(os.path.join('/home/rdogen/OpenClaw_Factory/projects/Hosteva', file))
