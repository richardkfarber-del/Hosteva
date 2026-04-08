from playwright.sync_api import Page, expect

def test_production_dashboard(page: Page):
    # Navigate to the dashboard
    page.goto("https://hosteva.onrender.com/dashboard")
    
    # Assert basic page load
    expect(page).to_have_title("Hosteva | Dashboard")
    expect(page.locator("text=Systems Status")).to_be_visible()
    
    # Specific button assertions (resolving strict mode violation)
    onboard_button = page.get_by_role("button", name="add Onboard")
    expect(onboard_button).to_be_visible()
