import os
import re

files = [
    "/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates/base.html",
    "/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates/dashboard.html"
]

for path in files:
    with open(path, "r") as f:
        content = f.read()

    # Replace user JS initials
    content = re.sub(r'<div class="w-8 h-8 rounded-full[^>]*>JS</div>', 
                     r'<div class="w-8 h-8 rounded-full bg-gradient-to-r from-[#75fbbf] to-[#52aecd] flex items-center justify-center font-bold text-on-surface text-sm" id="sidebar-user-initials">--</div>', content)
    
    # Replace John Smith
    content = re.sub(r'<p class="text-sm font-bold text-slate-800"[^>]*>John Smith</p>',
                     r'<p class="text-sm font-bold text-slate-800" id="sidebar-user-name">Loading...</p>', content)
    content = re.sub(r'<p class="text-sm font-bold text-slate-800">\s*John Smith\s*</p>',
                     r'<p class="text-sm font-bold text-slate-800" id="sidebar-user-name">Loading...</p>', content)
    
    # Replace Pro Host / Free Tier
    content = re.sub(r'<p class="text-xs text-\[#52aecd\]">Pro Host</p>',
                     r'<p class="text-xs text-[#52aecd]" id="sidebar-user-tier">...</p>', content)
    content = re.sub(r'<p class="text-xs text-\[#52aecd\]">Free Tier</p>',
                     r'<p class="text-xs text-[#52aecd]" id="sidebar-user-tier">...</p>', content)
    
    with open(path, "w") as f:
        f.write(content)

print("Dynamic user injection applied.")
