import os
import re

base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates"

files = ["base.html", "dashboard.html", "landing.html"]
for f in files:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        with open(path, "r") as file:
            content = file.read()
        
        # Logo replace
        content = re.sub(r'src="/static/img/hosteva_logo\.png"', r'src="{{ url_for(\'static\', path=\'img/hosteva_logo.png\') }}"', content)
        
        if f == "base.html" and "Integrations" not in content:
            dashboard_link = """<a class="flex items-center gap-3 py-3 px-4 text-slate-600 opacity-90 hover:bg-[#52aecd]/20 hover:opacity-100 transition-all font-medium rounded-lg {% if active_page == 'dashboard' %}bg-[#52aecd] text-white{% endif %}" href="{{ url_for('dashboard') }}">
                    <span class="material-symbols-outlined">dashboard</span>
                    <span>Host Dashboard</span>
                </a>"""
            integrations_link = """
                <a class="flex items-center gap-3 py-3 px-4 text-slate-600 opacity-90 hover:bg-[#52aecd]/20 hover:opacity-100 transition-all font-medium rounded-lg {% if active_page == 'integrations' %}bg-[#52aecd] text-white{% endif %}" href="/integrations">
                    <span class="material-symbols-outlined">extension</span>
                    <span>Integrations</span>
                </a>"""
            content = content.replace(dashboard_link, dashboard_link + integrations_link)
        
        content = content.replace('href="javascript:void(0)"', 'href="#"')

        js_script = """<script>
    document.addEventListener("DOMContentLoaded", async function() {
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            let userName = "Guest";
            let userTier = "Free Tier";
            let userInitials = "G";
            
            if (token) {
                const response = await fetch("/api/v1/users/me", {
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    userName = data.full_name || data.username || "User";
                    userTier = data.tier || "Free Tier";
                    userInitials = userName.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
                }
            }
            document.getElementById("sidebar-user-name").textContent = userName;
            document.getElementById("sidebar-user-tier").textContent = userTier;
            document.getElementById("sidebar-user-initials").textContent = userInitials;
        } catch (e) {
            document.getElementById("sidebar-user-name").textContent = "Guest";
            document.getElementById("sidebar-user-tier").textContent = "Free Tier";
            document.getElementById("sidebar-user-initials").textContent = "G";
        }
    });
    </script>
</body>"""

        if f in ["base.html", "dashboard.html"]:
            if "fetch(\"/api/v1/users/me\"" not in content:
                # Replace only the LAST </body> occurrence
                parts = content.rsplit("</body>", 1)
                if len(parts) == 2:
                    content = parts[0] + js_script + parts[1]

        with open(path, "w") as file:
            file.write(content)

print("UI fixes applied")
