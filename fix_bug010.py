import os
import re

base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates"
files = ["base.html", "dashboard.html", "landing.html", "wizard.html", "compliance_chat.html"]

for f in files:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        with open(path, "r") as file:
            content = file.read()
        
        # fix backslashes
        content = content.replace(r"this.src=\'https://placehold.co/200x80/006576/ffffff?text=Hosteva\';", "this.src='https://placehold.co/200x80/006576/ffffff?text=Hosteva';")
        
        with open(path, "w") as file:
            file.write(content)

print("Backslash fix applied.")
