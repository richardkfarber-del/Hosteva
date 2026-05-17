from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import os
from threading import Thread
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard", name="dashboard")
async def get_dashboard():
    return {"status": "ok"}
    
@app.get("/integrations", name="integrations")
async def get_integrations():
    return {"status": "ok"}

@app.get("/compliance_chat")
async def get_chat(request: Request):
    return templates.TemplateResponse(request, "compliance_chat.html", {"request": request})

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

t = Thread(target=run_server, daemon=True)
t.start()
time.sleep(2) # wait for server to start

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:8001/compliance_chat")
    time.sleep(1) # Wait for JS to execute / layout to settle
    os.makedirs("marketing/snapshots", exist_ok=True)
    page.screenshot(path="marketing/snapshots/FEAT-015_Gemini_Chat_UI.png", full_page=True)
    browser.close()
