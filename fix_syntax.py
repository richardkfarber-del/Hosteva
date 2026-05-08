import glob
import os

for file in glob.glob('/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_*.py'):
    with open(file, 'r') as f:
        content = f.read()
    
    bad_code = '    return f"{rules}" + "\n\n=== PAST MEMORY & EXPERTISE ===\n" + f"{memory}" + "\n\n=== CRITICAL DIRECTIVE ===\n\nThe above is your PAST memory. You must retain the technical expertise, but DO NOT rebuild past features.\n\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below.\n"'
    
    good_code = '    return f"{rules}\\n\\n=== PAST MEMORY & EXPERTISE ===\\n{memory}\\n\\n=== CRITICAL DIRECTIVE ===\\n\\nThe above is your PAST memory. You must retain the technical expertise, but DO NOT rebuild past features.\\n\\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below.\\n"'
    
    if bad_code in content:
        content = content.replace(bad_code, good_code)
        with open(file, 'w') as f:
            f.write(content)
        print(f"Fixed {file}")
    else:
        # Let's do a more robust regex replacement
        import re
        pattern = r'return f"\{rules\}" \+ "\n\n=== PAST MEMORY & EXPERTISE ===\n" \+ f"\{memory\}" \+ "\n\n=== CRITICAL DIRECTIVE ===\n\nThe above is your PAST memory\. You must retain the technical expertise, but DO NOT rebuild past features\.\n\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below\.\n"'
        if re.search(pattern, content):
            content = re.sub(pattern, good_code, content)
            with open(file, 'w') as f:
                f.write(content)
            print(f"Fixed {file} via regex")
