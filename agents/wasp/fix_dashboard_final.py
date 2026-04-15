import re

with open('../../templates/dashboard.html', 'r') as f:
    html = f.read()

# Replace logo
html = re.sub(r'<img src="/static/img/hosteva_logo\.png"', r'<img src="{{ url_for(\'static\', path=\'img/hosteva_logo.png\') }}"', html)

# Fix conflicting classes
# hidden flex -> hidden
html = re.sub(r'(id="add-property-modal"[^>]*?class="[^"]*?)hidden flex([^"]*?")', r'\1hidden\2', html)
html = re.sub(r'(id="filter-modal"[^>]*?class="[^"]*?)hidden flex([^"]*?")', r'\1hidden\2', html)

# remove text-white text-gray-800 from address-search
html = re.sub(r'(id="address-search"[^>]*?class="[^"]*?)text-white([^"]*?")', r'\1\2', html)
html = re.sub(r'(id="address-search"[^>]*?class="[^"]*?)text-gray-800([^"]*?")', r'\1\2', html)

# Fix duplicate spacing if any
html = html.replace('  ', ' ')

# Extract extra head (Leaflet CSS and custom <style>)
head_match = re.search(r'(<link rel="stylesheet" href="https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.css" />.*?</style>\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/dompurify/3\.0\.5/purify\.min\.js"></script>)', html, re.DOTALL)
extra_head = head_match.group(1) if head_match else ""

# Extract everything between <body> and </body>, then clean it up
body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
body_content = body_match.group(1) if body_match else ""

# Remove <aside>
body_content = re.sub(r'<aside.*?</aside>', '', body_content, flags=re.DOTALL)

# Remove the duplicate user fetching script
body_content = re.sub(r'<script>\s*document\.addEventListener\("DOMContentLoaded", async function\(\) \{.*?\}\);\s*</script>', '', body_content, flags=re.DOTALL)

# Remove md:ml-[260px] from header and main because base.html handles it
body_content = body_content.replace('md:ml-[260px]', '')

# Extract scripts (leaflet JS and dashboard scripts)
script_match = re.search(r'(<script src="https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.js"></script>\s*<script>.*?</script>)', body_content, re.DOTALL)
scripts = script_match.group(1) if script_match else ""

if scripts:
    body_content = body_content.replace(scripts, '')

# Construct new dashboard
new_dashboard = f"""{{% extends "base.html" %}}

{{% block title %}}Hosteva | Dashboard{{% endblock %}}

{{% block extra_head %}}
{extra_head}
{{% endblock %}}

{{% block header_title %}}Host Dashboard{{% endblock %}}

{{% block content %}}
{body_content.strip()}
{{% endblock %}}

{{% block scripts %}}
{scripts.strip()}
{{% endblock %}}
"""

with open('../../templates/dashboard.html', 'w') as f:
    f.write(new_dashboard)

