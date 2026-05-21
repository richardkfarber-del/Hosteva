import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Open local HTML directly or serve it
        html_path = "file://" + os.path.abspath("templates/compliance_chat.html")
        await page.goto(html_path)
        os.makedirs("marketing/snapshots", exist_ok=True)
        await page.screenshot(path="marketing/snapshots/FEAT-015_Gemini_Chat_UI.png", full_page=True)
        await browser.close()

asyncio.run(main())
