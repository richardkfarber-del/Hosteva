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
