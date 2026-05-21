import re

with open("project_board.md", "r") as f:
    content = f.read()

content = re.sub(r'### CHORE-(\d{3}): (.*)\*\*', r'### CHORE-\1: \2', content)

with open("project_board.md", "w") as f:
    f.write(content)
