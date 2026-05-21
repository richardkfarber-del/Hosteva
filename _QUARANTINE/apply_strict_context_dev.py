import os

def patch_file(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Replace load_system_prompt directive to strictly isolate context
        if '=== CRITICAL DIRECTIVE ===' in content:
            # Find the def load_system_prompt function and replace it
            import re
            pattern = r'def load_system_prompt\(.*?return f".*?=== CRITICAL DIRECTIVE ===.*?"\n'
            replacement = """def load_system_prompt(agent_name):
    rules = load_golden_rules(agent_name)
    return f"{rules}\\n\\n=== CRITICAL DIRECTIVE ===\\n\\nThe project root directory is: /home/rdogen/OpenClaw_Factory/projects/Hosteva/. Write all files using this absolute path. Your CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below. DO NOT reference past telemetry, failed tests, or downstream artifacts.\\n"
"""
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Patched {filepath}")
    except Exception as e:
        print(f"Error patching {filepath}: {e}")

files = [
    'run_05_development.py'
]

for file in files:
    patch_file(os.path.join('/home/rdogen/OpenClaw_Factory/projects/Hosteva', file))
