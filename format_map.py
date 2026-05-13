import os

with open('project_structure.txt', 'r') as f:
    lines = f.read().splitlines()

tree = {}
for line in lines:
    parts = line.split('/')
    current = tree
    for part in parts:
        if part not in current:
            current[part] = {}
        current = current[part]

def print_tree(d, indent=0):
    out = ""
    for k, v in sorted(d.items()):
        out += "  " * indent + f"- **`{k}`**\n"
        if v:
            out += print_tree(v, indent + 1)
    return out

markdown_tree = "# Hosteva Application Architecture Map\n\n" + print_tree(tree)

with open('REPO_MAP.md', 'w') as f:
    f.write(markdown_tree)
