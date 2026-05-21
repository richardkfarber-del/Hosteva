import os

artifact_map = {
    '03': '03_planning_poker_artifact.md',
    '04': '04_environment_artifact.md',
    '05': '05_development_artifact.md',
    '06': '06_qa_artifact.md',
    '07': '07_shadow_ops_artifact.md',
    '08': '08_retrospective_artifact.md'
}

for i in range(3, 9):
    num = f"0{i}"
    filename = f"/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_audit_{num}.py"
    if not os.path.exists(filename): continue
    with open(filename, 'r') as f:
        content = f.read()
    
    if 'def read_artifact' not in content:
        replacement = """def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f'ERROR: {filename} missing.'

def read_artifact(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
            content = f.read()
            return content.replace('{', '{{').replace('}', '}}')
    except FileNotFoundError:
        return "ERROR: Artifact missing."
"""
        content = content.replace("def load_prompt(filename):\n    try:\n        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:\n            return f.read()\n    except FileNotFoundError:\n        return f'ERROR: {filename} missing.'\n", replacement)
    
    art_file = artifact_map[num]
    old_prompt = f"prompt='Audit Phase {num} artifacts'"
    new_prompt = f"prompt=f'Audit the following Phase {num} artifacts:\n\n{{read_artifact(\"{art_file}\")}}'"
    content = content.replace(old_prompt, new_prompt)
    
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Patched {filename}")
