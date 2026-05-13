import sys

filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/heimdall/SKILL.md"
with open(filepath, 'r') as f:
    content = f.read()

old_str = 'verifying the Git staging area/commit, ensuring no local syntax regressions exist, and formally approving the local mainline merge. Do NOT search for Render configurations or Cloudflare caching for Path B tickets. Verify the physical code locally and return a success status to close the gate.'
new_str = 'verifying the Git staging area (`git diff --staged`), ensuring no local syntax regressions exist, and formally executing `git commit -m "[Ticket-ID] Deployment Approved"` to merge the code. Do NOT search for Render configurations or Cloudflare caching for Path B tickets. Verify the staged physical code, commit it, and return a success status to close the gate.'

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Heimdall updated successfully.")
else:
    print("Old string not found in Heimdall SKILL.md")
