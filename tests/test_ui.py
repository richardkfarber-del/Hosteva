import pytest

def test_dashboard_ui_frameworks():
    with open("templates/dashboard.html", "r") as f:
        html = f.read()
    assert "cdn.tailwindcss.com" in html
    assert "fonts.googleapis.com" in html
    assert "stark-red" not in html
    assert "stark-black" not in html
    
def test_landing_ui_frameworks():
    with open("templates/landing.html", "r") as f:
        html = f.read()
    assert "cdn.tailwindcss.com" in html
    assert "fonts.googleapis.com" in html
    assert "stark-red" not in html
    assert "stark-black" not in html
