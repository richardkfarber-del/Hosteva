import os
import sys
from playwright.sync_api import sync_playwright

def run_uat():
    print("Starting Black Widow UAT Browser Automation...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to https://hosteva.onrender.com/pricing...")
            response = page.goto("https://hosteva.onrender.com/pricing", timeout=60000)
            print(f"HTTP Status: {response.status}")
            print(f"Page Title: {page.title()}")
            content = page.content().lower()
            if "stripe" in content or "subscribe" in content or "pricing" in page.url.lower() or "plan" in page.url.lower():
                print("UAT SUCCESS: Pricing UI loaded successfully.")
            else:
                print("UAT WARNING: Page loaded, but pricing/subscription elements not found in the DOM.")
        except Exception as e:
            print(f"UAT FAILED: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    try:
        run_uat()
    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)
