import re
with open('../../templates/dashboard.html', 'r') as f:
    content = f.read()
classes = re.findall(r'class="([^"]*)"', content)
for c in classes:
    words = c.split()
    dupes = set([w for w in words if words.count(w) > 1])
    if dupes:
        print(f"Duplicates {dupes} in: {c}")
