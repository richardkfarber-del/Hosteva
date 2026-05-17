with open('templates/base.html', 'r') as f:
    content = f.read()
content = content.replace("{{ url_for('static', path='img/hosteva_logo.png') }}", "/static/img/hosteva_logo.png")
with open('templates/base.html', 'w') as f:
    f.write(content)

with open('templates/landing.html', 'r') as f:
    content = f.read()
content = content.replace("{{ url_for('static', path='img/hosteva_logo.png') }}", "/static/img/hosteva_logo.png")
with open('templates/landing.html', 'w') as f:
    f.write(content)

