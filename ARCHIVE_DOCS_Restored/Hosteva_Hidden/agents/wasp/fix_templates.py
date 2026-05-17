import re

# 1. Fix logos in base.html and landing.html
for filepath in ['../../templates/base.html', '../../templates/landing.html']:
    with open(filepath, 'r') as f:
        content = f.read()
    content = re.sub(r'<img src="/static/img/hosteva_logo\.png"', r'<img src="{{ url_for(\'static\', path=\'img/hosteva_logo.png\') }}"', content)
    with open(filepath, 'w') as f:
        f.write(content)

# 2. Refactor dashboard.html
with open('../../templates/dashboard.html', 'r') as f:
    content = f.read()

# Replace logo just in case
content = re.sub(r'<img src="/static/img/hosteva_logo\.png"', r'<img src="{{ url_for(\'static\', path=\'img/hosteva_logo.png\') }}"', content)

# Remove everything before <style> block and replace with extends
# Actually, the extra_head block should contain Leaflet CSS and custom styles
head_content_match = re.search(r'<link rel="stylesheet" href="https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.css" />.*?<style>.*?</style>\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/dompurify/3\.0\.5/purify\.min\.js"></script>', content, re.DOTALL)
extra_head = head_content_match.group(0) if head_content_match else ""

# Extract modlas and main content
# Wait, dashboard.html has:
# <div id="add-property-modal" ...
# <div id="filter-modal" ...
# <main ...
# We need to extract the modals and the main content.
# Actually, in base.html, where does `{% block content %}` sit?
