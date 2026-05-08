import re

# Fix pricing.py
pricing_path = 'app/routers/pricing.py'
with open(pricing_path, 'r') as f:
    p_content = f.read()
p_content = p_content.replace('templates.TemplateResponse("pricing.html", {"request": request})', 'templates.TemplateResponse(request=request, name="pricing.html", context={"request": request})')
with open(pricing_path, 'w') as f:
    f.write(p_content)

# Fix main.py
main_path = 'app/main.py'
with open(main_path, 'r') as f:
    m_content = f.read()

# Replace the malformed line
# We use a regex to catch the malformed part without needing the exact redacted text
m_content = re.sub(r'"google_maps_"api_key": ".*?\("GOOGLE_MAPS_API_KEY", ""\)', '"google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY", "")', m_content)

with open(main_path, 'w') as f:
    f.write(m_content)

# Fix uat_live_pricing.py
uat_path = 'tests/uat_live_pricing.py'
with open(uat_path, 'r') as f:
    u_content = f.read()
u_content = u_content.replace('content = page.content().lower()\n            if response.status != 200:', 'if response.status != 200:\n                print(f"UAT FAILED: Expected HTTP 200, got {response.status}")\n                sys.exit(1)\n            content = page.content().lower()')
with open(uat_path, 'w') as f:
    f.write(u_content)

print("Fixes applied.")
