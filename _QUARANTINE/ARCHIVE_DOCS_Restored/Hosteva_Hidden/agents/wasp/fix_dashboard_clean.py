import re

with open('../../templates/dashboard.html', 'r') as f:
    html = f.read()

# Replace logo
html = re.sub(r'<img src="/static/img/hosteva_logo\.png"', r'<img src="{{ url_for(\'static\', path=\'img/hosteva_logo.png\') }}"', html)

# Strip conflicting classes
# #add-property-modal
html = re.sub(r'(id="add-property-modal"[^>]*?) hidden flex', r'\1 hidden', html)
# #filter-modal
html = re.sub(r'(id="filter-modal"[^>]*?) hidden flex', r'\1 hidden', html)
# #address-search
html = re.sub(r'(id="address-search"[^>]*?) text-white', r'\1', html)
html = re.sub(r'(id="address-search"[^>]*?) text-gray-800', r'\1', html)

# Extract sections
head_match = re.search(r'(<link rel="stylesheet" href="https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.css" />.*?</style>\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/dompurify/3\.0\.5/purify\.min\.js"></script>)', html, re.DOTALL)
extra_head = head_match.group(1) if head_match else ""

# Get everything inside body EXCEPT the sidebar (<aside>...</aside>)
body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
body_content = body_match.group(1) if body_match else ""

# Remove the <aside> from body_content
body_content = re.sub(r'<aside.*?</aside>', '', body_content, flags=re.DOTALL)

# Also remove md:ml-[260px] from everything because base.html already handles it
body_content = body_content.replace('md:ml-[260px]', '')

# Dashboard had a <header> and a <main>. In base.html, {% block content %} is inside a <main> div.
# But just keeping them as is (minus the ml margin) is fine for now, or just leave it.

# Actually, the user just asked to use extends, remove duplicate head and inline Tailwind scripts, and strip specific classes.
# I will wrap the remaining body in {% block content %} and {% block scripts %}

# Split scripts
script_match = re.search(r'(<script src="https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.js"></script>\s*<script>.*?</script>)', body_content, re.DOTALL)
scripts = script_match.group(1) if script_match else ""

# Remove scripts from body_content
if scripts:
    body_content = body_content.replace(scripts, '')

# There's another script at the end about sidebar-user-name, which we might want to keep or it's duplicated from base.html.
# Actually base.html has the user info fetching. Wait, let's check base.html if it has the fetch("/api/v1/users/me").
