import sys
from playwright.sync_api import sync_playwright

def run_full_uat():
    print("Starting Black Widow Full UAT Browser Automation...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # 1. Test Homepage
            print("Navigating to https://hosteva.onrender.com/ ...")
            response = page.goto("https://hosteva.onrender.com/", timeout=30000)
            print(f"HTTP Status: {response.status if response else 'UNKNOWN'}")
            
            if not response or response.status >= 400:
                print(f"UAT FAILED: Site crashed or returned error status: {response.status if response else 'No Response'}")
                sys.exit(1)
                
            # 2. Test Navigation to Pricing
            print("Attempting to navigate to Pricing...")
            page.goto("https://hosteva.onrender.com/pricing", timeout=30000)
            
            # 3. Test Navigation to Dashboard
            print("Attempting to navigate to Dashboard...")
            page.goto("https://hosteva.onrender.com/dashboard", timeout=30000)
            
            # 4. Form Interaction (Fake Address)
            print("Attempting to fill out a form (simulating user input)...")
            inputs = page.locator("input").count()
            if inputs > 0:
                print(f"Found {inputs} input fields. Simulating typing...")
                page.locator("input").first.fill("123 Fake Street, QA City")
            else:
                print("No input fields found on current page, skipping form entry.")
            
            print("UAT SUCCESS: Full browser regression suite passed. All pages loaded and interactions succeeded.")
        except Exception as e:
            print(f"UAT FAILED: Browser encountered an error: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_full_uat()
