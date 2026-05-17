import os

def remove_dupe(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    to_remove = """    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>

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
</script>"""

    if to_remove in content:
        content = content.replace(to_remove, "")
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Cleaned {filepath}")
    else:
        print(f"Not found in {filepath}")

remove_dupe('/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates/landing.html')
remove_dupe('/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates/dashboard.html')
