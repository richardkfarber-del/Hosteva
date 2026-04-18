"""
Test Suite for MVP Dashboard UI (dashboard.html)
Implements FEAT-019 TDD Mandate verifying PropertyCardSkeleton rendering and System Degraded state.
Written by Wasp (simulated/instantiated by Architect).
"""

import pytest
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "templates", "dashboard.html")

def test_dashboard_skeleton_rendering():
    with open(TEMPLATE_PATH, "r") as f:
        html_content = f.read()
    assert 'class="PropertyCardSkeleton animate-pulse"' in html_content

def test_dashboard_system_degraded_rendering():
    with open(TEMPLATE_PATH, "r") as f:
        html_content = f.read()
    assert 'class="error-title">System Degraded</h1>' in html_content

def test_dashboard_ui_component_contract():
    # Architect's explicit verification: strict contract check
    with open(TEMPLATE_PATH, "r") as f:
        html_content = f.read()
    assert 'id="property-list"' in html_content