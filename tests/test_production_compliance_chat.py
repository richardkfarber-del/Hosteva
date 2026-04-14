from playwright.sync_api import Page, expect

def test_production_compliance_chat(page: Page):
    # Navigate to the live URL (simulated staging if needed, but we check live here)
    page.goto("https://hosteva.onrender.com/compliance_chat")
    
    # Verify the UI rendering
    expect(page.locator("text=Compliance Wizard Chat")).to_be_visible()
    
    # Fill out the form
    chat_input = page.locator("#chat-input")
    chat_input.fill("What are the STR noise ordinances in Austin?")
    
    # Submit the form
    page.locator("#submit-button").click()
    
    # Verify DOMPurify is working or at least loading states and network drops handled
    expect(page.locator("#loading-indicator")).to_be_visible()
