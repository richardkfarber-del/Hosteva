import os
import re
import glob

# 1. & 3. Fix UUIDs and Context Bleed
for filepath in glob.glob('/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_*.py'):
    with open(filepath, 'r') as f:
        content = f.read()
    
    new_content = content
    # Fix UUIDs
    new_content = re.sub(r"append_to_ledger\(f'KICKBACK triggered by \{k\}'\)", "append_to_ledger('KICKBACK triggered')", new_content)
    
    # Context bleed
    if 'load_system_prompt' in new_content and '=== CRITICAL DIRECTIVE ===' not in new_content:
        new_content = new_content.replace('return rules', 'return rules + "\\n\\n=== CRITICAL DIRECTIVE ===\\n\\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below. DO NOT reference past test failures or external logs.\\n"')

    # Add UUID mapping if not present
    if 'ids = {' in new_content and 'id_to_name =' not in new_content:
        new_content = re.sub(r"(ids = \{.*?\}\n)", r"\1id_to_name = {v: k for k, v in ids.items()}\n", new_content, flags=re.DOTALL)
        new_content = new_content.replace("f'# {k}\\n{v}\\n\\n'", "f'# {id_to_name.get(k, k)}\\n{v}\\n\\n'")

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Patched {filepath}")

# 2. Fix Coulson 3-Strike
coulson_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_coulson_intervention.py'
with open(coulson_path, 'r') as f:
    coulson = f.read()
    
strike_logic = """def count_consecutive_kickbacks():
    strike_file = os.path.join(os.path.dirname(__file__), 'strike_counter.txt')
    count = 0
    if os.path.exists(strike_file):
        with open(strike_file, 'r') as f:
            try:
                count = int(f.read().strip())
            except:
                pass
    count += 1
    with open(strike_file, 'w') as f:
        f.write(str(count))
    return count
"""
coulson = re.sub(r'def count_consecutive_kickbacks\(\):.*?return 0', strike_logic, coulson, flags=re.DOTALL)
with open(coulson_path, 'w') as f:
    f.write(coulson)
print("Patched run_coulson_intervention.py")
