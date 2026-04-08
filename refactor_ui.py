import os
import re

TEMPLATES_DIR = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates'

TAILWIND_CONFIG = """
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        'surface': '#f8f9ff',
        'surface-container-low': '#eff4ff',
        'surface-container-lowest': '#ffffff',
        'surface-container-high': '#dce9ff',
        'primary': '#006576',
        'primary-container': '#1c7f92',
        'on-surface': '#001c37',
        'outline-variant': '#bec8cc',
        'tertiary-fixed': '#75fbbf'
      },
      fontFamily: {
        'display': ['Manrope', 'sans-serif'],
        'headline': ['Manrope', 'sans-serif'],
        'body': ['Inter', 'sans-serif']
      },
      boxShadow: {
        'ambient': '0 20px 40px rgba(0, 28, 55, 0.08)',
        'ambient-light': '0 20px 40px rgba(0, 28, 55, 0.04)'
      }
    }
  }
}
</script>
"""

FONTS_RE = re.compile(r'<link[^>]*href="https://fonts\.googleapis\.com/css2\?family=Inter[^>]*>', re.IGNORECASE)
NEW_FONTS = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>'

TAILWIND_SCRIPT_RE = re.compile(r'<script src="https://cdn\.tailwindcss\.com[^>]*></script>', re.IGNORECASE)
EXISTING_CONFIG_RE = re.compile(r'<script id="tailwind-config">.*?</script>', re.DOTALL)

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Fonts
    if FONTS_RE.search(content):
        content = FONTS_RE.sub(NEW_FONTS, content)

    # Tailwind Config
    content = EXISTING_CONFIG_RE.sub('', content)
    
    # Insert new tailwind config right after the tailwind script
    match = TAILWIND_SCRIPT_RE.search(content)
    if match:
        content = content[:match.end()] + "\n" + TAILWIND_CONFIG + content[match.end():]

    # Global Replacements for Colors & Borders
    # Prohibit 1px borders
    content = re.sub(r'\bborder-slate-\d+\b', '', content)
    content = re.sub(r'\bborder-gray-\d+\b', '', content)
    content = re.sub(r'\bborder-teal-\d+\b', '', content)
    content = re.sub(r'\bborder\b(?!-l-\[3px\])(?!-tertiary-fixed)', '', content) # Remove general border
    content = re.sub(r'\bborder-[trbl]\b(?!-l-\[3px\])', '', content) 
    content = re.sub(r'\bshadow-sm\b', 'shadow-ambient-light', content)
    content = re.sub(r'\bshadow-md\b', 'shadow-ambient', content)
    content = re.sub(r'\bshadow-lg\b', 'shadow-ambient', content)
    
    # Surface colors
    content = re.sub(r'\bbg-slate-50\b', 'bg-surface-container-low', content)
    content = re.sub(r'\bbg-gray-50\b', 'bg-surface-container-low', content)
    content = re.sub(r'\bbg-white\b', 'bg-surface-container-lowest', content)
    
    # Primary CTA
    content = re.sub(r'\bbg-teal-600\b', 'bg-gradient-to-br from-primary to-primary-container', content)
    content = re.sub(r'\bbg-teal-700\b', 'bg-gradient-to-br from-primary to-primary-container', content)
    content = re.sub(r'\btext-teal-600\b', 'text-primary', content)
    content = re.sub(r'\btext-teal-700\b', 'text-primary', content)
    
    # Text colors
    content = re.sub(r'\btext-slate-900\b', 'text-on-surface font-headline tracking-tight', content)
    content = re.sub(r'\btext-gray-900\b', 'text-on-surface font-headline tracking-tight', content)

    # Button radius
    content = re.sub(r'\brounded-md\b', 'rounded-[8px]', content)
    content = re.sub(r'\brounded-lg\b', 'rounded-[8px]', content)

    with open(filepath, 'w') as f:
        f.write(content)

for root, _, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if file.endswith('.html'):
            process_file(os.path.join(root, file))

