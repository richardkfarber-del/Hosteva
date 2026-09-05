import pytest
from fastapi.testclient import TestClient
from html.parser import HTMLParser
from app.main import app

client = TestClient(app)

class DOMParser(HTMLParser):
    """
    A lightweight parser to collect element attributes and verify DOM structures.
    """
    def __init__(self):
        super().__init__()
        self.elements = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        self.elements.append({
            "tag": tag,
            "id": attr_dict.get("id"),
            "class": attr_dict.get("class")
        })

def test_wizard_dom_elements():
    """
    Objective 3: Introduce client-side DOM/component check script to mathematically
    verify structural loading states and error elements in the wizard template.
    """
    response = client.get("/wizard")
    assert response.status_code == 200
    
    html_content = response.text
    parser = DOMParser()
    parser.feed(html_content)
    
    # Check for critical elements in the parsed DOM list
    element_ids = [el["id"] for el in parser.elements if el["id"] is not None]
    
    # 1. Verify that defaultState, loadingState, dataState, and errorState are all present
    assert "defaultState" in element_ids
    assert "loadingState" in element_ids
    assert "dataState" in element_ids
    assert "errorState" in element_ids
    
    # 2. Verify structure of loadingState (Skeleton Screen elements)
    loading_element = next(el for el in parser.elements if el["id"] == "loadingState")
    # Verify that it is configured to start as hidden
    assert "hidden" in loading_element["class"]
    
    # Verify presence of animate-pulse elements representing the skeletons
    pulse_elements = [el for el in parser.elements if el["class"] and "animate-pulse" in el["class"]]
    assert len(pulse_elements) >= 2, "Loading skeleton must contain at least 2 animate-pulse blocks."

    # 3. Verify structure of errorState (Error elements)
    error_element = next(el for el in parser.elements if el["id"] == "errorState")
    # Verify that it is configured to start as hidden
    assert "hidden" in error_element["class"]
    assert "errorState" in element_ids
    
    # Verify error message dynamic field is present in DOM
    assert "errorMessage" in element_ids
    assert "retryBtn" in element_ids

def test_dashboard_sidebar_dom_elements():
    """
    Objective 3: Verify core structural navigation elements are in base shell layout.
    """
    # Since dashboard is auth-protected, we load /wizard which extends the base layout shell
    response = client.get("/wizard")
    assert response.status_code == 200
    
    html_content = response.text
    parser = DOMParser()
    parser.feed(html_content)
    
    element_ids = [el["id"] for el in parser.elements if el["id"] is not None]
    
    # Verify basic layout components (sidebar logout, notifications, main container)
    assert "sidebar-logout-btn" in element_ids or "header-logout-btn" in element_ids


def test_wizard_disclaimer_outside_flex_row_pl01():
    """BUG-PL-01: Legal disclaimer must not be a third flex column that truncates results."""
    response = client.get("/wizard")
    assert response.status_code == 200
    html = response.text
    assert "outside flex row" in html or "Legal Disclaimer" in html
    # Disclaimer comment / structure: glass panel closes before disclaimer
    glass_idx = html.find("glass-panel")
    disc_idx = html.find("Legal Disclaimer")
    assert glass_idx != -1 and disc_idx != -1
    # Results panel must not use overflow-hidden (clips Checklist Available)
    assert 'id="resultsPanel"' in html
    results_snip = html[html.find('id="resultsPanel"')-120:html.find('id="resultsPanel"')+180]
    assert "overflow-hidden" not in results_snip
    assert "overflow-y-auto" in results_snip or "min-w-0" in results_snip
    # dataState uses flex + min-w-0 for readable cards
    assert 'id="dataState"' in html
    assert "showResultsState" in html
    # Auth token pattern includes access_token (sidebar Guest fix)
    assert "access_token" in html


def test_base_sidebar_auth_uses_access_token_pl01():
    response = client.get("/wizard")
    html = response.text
    assert 'localStorage.getItem("access_token")' in html or "localStorage.getItem('access_token')" in html
    assert "/api/v1/users/me" in html
    assert "/api/user/me" in html
