import sys
import os

def verify():
    path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/templates/dashboard.html"
    with open(path, "r") as f:
        content = f.read()
    
    # Check if the duplicate DOMContentLoaded script is inside the exportPDF string
    if "document.getElementById(\"sidebar-user-name\").textContent = userName;" in content.split("function exportPDF(propertyId)")[1].split("printWindow.document.write(html);")[0]:
        print("FAIL: The duplicate script block is still inside the exportPDF template literal.")
        sys.exit(1)
        
    print("SUCCESS: BUG-001 template literal leakage fix verified locally.")

if __name__ == "__main__":
    verify()
