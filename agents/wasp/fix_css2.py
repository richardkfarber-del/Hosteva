import os

def remove_style(filepath, to_remove):
    with open(filepath, 'r') as f:
        content = f.read()

    if to_remove in content:
        content = content.replace(to_remove, "")
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Cleaned {filepath}")
    else:
        print(f"Not found in {filepath}")

landing_style = """    <style>
            .material-symbols-outlined {
                font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
            }"""

dashboard_style = """    <style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
            vertical-align: middle;
        }"""

remove_style('/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates/landing.html', landing_style)
remove_style('/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates/dashboard.html', dashboard_style)
