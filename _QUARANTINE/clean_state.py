import json

path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json'
with open(path, 'r') as f:
    data = json.load(f)

data['input'] = "# BUG-002: Persistent Broken Logo\n\n## Description\nFix the broken image links by replacing hardcoded HTML paths (e.g., `<img src=\"/static/img/hosteva_logo.png\">`) with proper Jinja2 dynamic routing (e.g., `<img src=\"{{ url_for('static', filename='img/hosteva_logo.png') }}\">`) globally across the repository so the logo renders correctly regardless of the route depth.\n\n## Expected Behavior\nThe logo should render correctly on all pages, using Jinja2 `url_for`.\n"

with open(path, 'w') as f:
    json.dump(data, f, indent=4)
print('State cleaned!')
