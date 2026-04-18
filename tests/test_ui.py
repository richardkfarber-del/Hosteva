import pytest
import re

def test_dashboard_ui_frameworks():
    with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/templates/dashboard.html", "r") as f:
        html = f.read()
    assert "cdn.tailwindcss.com" in html
    assert "fonts.googleapis.com" in html
    
def test_landing_ui_frameworks():
    try:
        with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/templates/landing.html", "r") as f:
            html = f.read()
        assert "cdn.tailwindcss.com" in html
        assert "fonts.googleapis.com" in html
    except FileNotFoundError:
        pass # Optional if landing.html doesn't exist

def test_dashboard_property_card_skeleton():
    with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/templates/dashboard.html", "r") as f:
        html = f.read()
    
    # Use regex to find the <template id="property-card-skeleton">...</template> block
    match = re.search(r'<template\s+id="property-card-skeleton"[^>]*>([\s\S]*?)</template>', html, re.IGNORECASE)
    assert match is not None, "PropertyCardSkeleton template missing"
    
    template_content = match.group(1)
    assert 'animate-pulse' in template_content, "Skeleton must have animate-pulse class"
    assert 'bg-gray-' in template_content, "Skeleton must have background placeholders"

def test_dashboard_system_degraded_boundary():
    with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/templates/dashboard.html", "r") as f:
        html = f.read()
    
    # Use regex to find the <template id="system-degraded-error">...</template> block
    match = re.search(r'<template\s+id="system-degraded-error"[^>]*>([\s\S]*?)</template>', html, re.IGNORECASE)
    assert match is not None, "System Degraded error template missing"
    
    template_content = match.group(1)
    assert 'System Degraded' in template_content, "System Degraded text missing"
    assert 'cloud_off' in template_content, "System Degraded icon missing"
    assert 'material-symbols-outlined' in template_content, "System Degraded material icon class missing"

if __name__ == "__main__":
    print("Running tests locally...")
    test_dashboard_ui_frameworks()
    test_landing_ui_frameworks()
    test_dashboard_property_card_skeleton()
    test_dashboard_system_degraded_boundary()
    print("All UI DOM tests passed locally!")
