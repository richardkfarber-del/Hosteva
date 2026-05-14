import pytest

def test_jinja2_logo_render():
    files = [
        '/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/templates/dashboard.html',
        '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/templates/dashboard.html',
        '/home/rdogen/OpenClaw_Factory/projects/Hosteva/ARCHIVE_DOCS/Hosteva_Hidden/templates/dashboard.html'
    ]
    
    for file_path in files:
        with open(file_path, 'r') as file:
            content = file.read()
            assert "{{ url_for('static', filename='img/hosteva_logo.png') }}" in content, f"Jinja2 syntax not found in {file_path}"
