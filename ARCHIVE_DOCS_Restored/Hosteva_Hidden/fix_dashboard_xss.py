import os
import re

path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates/dashboard.html"

with open(path, "r") as file:
    content = file.read()

# Fix innerHTML assignments
content = content.replace("button.innerHTML = '<span", "button.innerHTML = DOMPurify.sanitize('<span")
content = content.replace(" Generating...';", " Generating...');")

content = content.replace("button.innerHTML = originalText;", "button.innerHTML = DOMPurify.sanitize(originalText);")

content = content.replace("contentDiv.innerHTML = '<p class=\"text-xs text-gray-500 animate-pulse\">Loading recommendations...</p>';", "contentDiv.innerHTML = DOMPurify.sanitize('<p class=\"text-xs text-gray-500 animate-pulse\">Loading recommendations...</p>');")

content = content.replace("contentDiv.innerHTML = '<p class=\"text-xs text-gray-600\">No recommendations available. Property is optimized!</p>';", "contentDiv.innerHTML = DOMPurify.sanitize('<p class=\"text-xs text-gray-600\">No recommendations available. Property is optimized!</p>');")

content = content.replace("contentDiv.innerHTML = '<p class=\"text-xs text-red-600\">Failed to load recommendations</p>';", "contentDiv.innerHTML = DOMPurify.sanitize('<p class=\"text-xs text-red-600\">Failed to load recommendations</p>');")

with open(path, "w") as file:
    file.write(content)

print("Dashboard innerHTML fixes applied")
