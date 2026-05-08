import re

with open('../../templates/dashboard.html', 'r') as f:
    html = f.read()

# Fix logo just in case
html = re.sub(r'<img src="/static/img/hosteva_logo\.png"', r'<img src="{{ url_for(\'static\', path=\'img/hosteva_logo.png\') }}"', html)

# Strip conflicting Tailwind classes ('hidden flex', 'text-white text-gray-800') from modals and search
# 1. #add-property-modal
html = re.sub(r'(id="add-property-modal"[^>]*?) hidden flex', r'\1 hidden', html)
# 2. #filter-modal
html = re.sub(r'(id="filter-modal"[^>]*?) hidden flex', r'\1 hidden', html)
# 3. #address-search
html = re.sub(r'(id="address-search"[^>]*?) text-white', r'\1', html)
html = re.sub(r'(id="address-search"[^>]*?) text-gray-800', r'\1', html)

# Now, we need to extract extra_head, modals, main content, and scripts
head_match = re.search(r'(<link rel="stylesheet" href="https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.css" />.*?</style>\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/dompurify/3\.0\.5/purify\.min\.js"></script>)', html, re.DOTALL)
extra_head = head_match.group(1) if head_match else ""

modal_1_match = re.search(r'(<div id="add-property-modal".*?</div>\s*</div>)', html, re.DOTALL)
modal_1 = modal_1_match.group(1) if modal_1_match else ""

modal_2_match = re.search(r'(<div id="filter-modal".*?</div>\s*</div>)', html, re.DOTALL)
modal_2 = modal_2_match.group(1) if modal_2_match else ""

# Extract the header inside dashboard.html, but wait, dashboard has its own <header> with #address-search
header_match = re.search(r'(<header class="md:ml-\[260px\].*?</header>)', html, re.DOTALL)
header_content = header_match.group(1) if header_match else ""

# The content inside <main>
main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
main_content = main_match.group(1) if main_match else ""

# The scripts at the end
script_match = re.search(r'(<script src="https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.js"></script>\s*<script>.*?</script>)', html, re.DOTALL)
scripts = script_match.group(1) if script_match else ""

new_dashboard = f"""{{% extends "base.html" %}}

{{% block title %}}Hosteva | Dashboard{{% endblock %}}

{{% block extra_head %}}
{extra_head}
{{% endblock %}}

{{% block header_title %}}Host Dashboard{{% endblock %}}

{{% block content %}}
<!-- Wait, the dashboard has its own custom search header. Let's see if we should include it. -->
<!-- Actually, let's just include the modals, header, and main content in the block content. -->
<!-- But base.html already has a <header>. If we just dump dashboard's header here, it might look weird. -->
<!-- Let's put everything dashboard had between <header> and </main> -->
{header_content}
{modal_1}
{modal_2}
{main_content}
{{% endblock %}}

{{% block scripts %}}
{scripts}
{{% endblock %}}
"""

with open('dashboard_new.html', 'w') as f:
    f.write(new_dashboard)

