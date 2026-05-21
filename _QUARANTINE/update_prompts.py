import glob
import re

old_pattern = r'return f"\{rules\}" \+ "\\n\\n=== YOUR INDIVIDUAL MEMORY & EXPERTISE ===\\n" \+ f"\{memory\}"'
new_str = 'return f"{rules}" + "\n\n=== PAST MEMORY & EXPERTISE ===\n" + f"{memory}" + "\n\n=== CRITICAL DIRECTIVE ===\n\\nThe above is your PAST memory. You must retain the technical expertise, but DO NOT rebuild past features.\n\\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below.\n"'

count = 0
for file in glob.glob("/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_*.py"):
    with open(file, "r") as f:
        content = f.read()
    
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_str, content)
        with open(file, "w") as f:
            f.write(content)
        print(f"Updated {file}")
        count += 1
print(f"Total files updated: {count}")
