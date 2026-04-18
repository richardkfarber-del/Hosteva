import re
with open("system/swarm_worker.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "prompt = f\"Refine this" in line or "prompt = f\"Run headless" in line or "prompt = f\"Deploy ticket" in line:
        line = line.replace("\n", "").replace("\\n", "\\n") + "\"\n"
        # actually let's just use raw python to write it safely.
    new_lines.append(line)

# Let's just sed replace the broken lines.
