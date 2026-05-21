import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://hosteva.onrender.com/dashboard")
        await page.wait_for_timeout(2000) # Give time for JS metrics to load
        await page.screenshot(path="live_dashboard.png", full_page=True)
        await browser.close()

asyncio.run(main())
