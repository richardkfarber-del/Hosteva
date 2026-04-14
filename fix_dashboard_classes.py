import re

with open('templates/dashboard.html', 'r') as f:
    content = f.read()

# Also do url_for
content = content.replace("{{ url_for('static', path='img/hosteva_logo.png') }}", "/static/img/hosteva_logo.png")

def clean_class(match):
    class_str = match.group(1)
    classes = class_str.split()
    unwanted = {'backdrop-blur-[20px]', 'shadow-ambient', 'backdrop-blur-md', 'backdrop-blur-xl', 'backdrop-blur-sm', 'border'}
    new_classes = []
    # keep track of seen so we also remove duplicates within the same class="..." list
    seen = set()
    for c in classes:
        if c not in unwanted:
            if c not in seen:
                new_classes.append(c)
                seen.add(c)
    return 'class="' + ' '.join(new_classes) + '"'

content = re.sub(r'class="([^"]*)"', clean_class, content)

def clean_js_class(match):
    class_str = match.group(1)
    classes = class_str.split()
    unwanted = {'backdrop-blur-[20px]', 'shadow-ambient', 'backdrop-blur-md', 'backdrop-blur-xl', 'backdrop-blur-sm', 'border'}
    new_classes = []
    seen = set()
    for c in classes:
        if c not in unwanted:
            if c not in seen:
                new_classes.append(c)
                seen.add(c)
    return "className = '" + ' '.join(new_classes) + "'"

content = re.sub(r"className = '([^']*)'", clean_js_class, content)

def clean_js_template(match):
    class_str = match.group(1)
    classes = class_str.split()
    unwanted = {'backdrop-blur-[20px]', 'shadow-ambient', 'backdrop-blur-md', 'backdrop-blur-xl', 'backdrop-blur-sm', 'border'}
    new_classes = []
    seen = set()
    for c in classes:
        if c not in unwanted:
            if c not in seen:
                new_classes.append(c)
                seen.add(c)
    return 'const base = "' + ' '.join(new_classes) + ' "'

content = re.sub(r'const base = "([^"]*)"', clean_js_template, content)

# One more case in JS template literals `<div class="...`
def clean_js_html_class(match):
    class_str = match.group(1)
    classes = class_str.split()
    unwanted = {'backdrop-blur-[20px]', 'shadow-ambient', 'backdrop-blur-md', 'backdrop-blur-xl', 'backdrop-blur-sm', 'border'}
    new_classes = []
    seen = set()
    for c in classes:
        if c not in unwanted:
            if c not in seen:
                new_classes.append(c)
                seen.add(c)
    return 'class="' + ' '.join(new_classes) + '"'

content = re.sub(r'class=\\"([^\\"]*)\\"', clean_js_html_class, content) # handle escaped quotes?
# The regex r'class="([^"]*)"' handles normal JS template literals where quotes are not escaped.

with open('templates/dashboard.html', 'w') as f:
    f.write(content)

