import uvicorn
from fastapi import FastAPI, Request
import multiprocessing

app1 = FastAPI()
app2 = FastAPI()

@app1.post("/state/update")
async def update_state(request: Request):
    data = await request.json()
    with open("test_state.log", "a") as f:
        f.write(f"STATE UPDATE: {data.get('ticket_id')} -> {data.get('status')}\n")
    return {"status": "ok"}

@app2.post("/mock_completions")
async def chat_completions(request: Request):
    data = await request.json()
    model = data.get("model", "")
    messages = data.get("messages", [])
    prompt = messages[0]["content"] if messages else ""
    
    if "iron_man" in model:
        content = "Mock execution output."
    elif "coulson" in model:
        if "TEST-HAPPY" in prompt:
            content = "VERIFIED"
        elif "TEST-STRIKE" in prompt:
            content = "REJECTED: Mock failure"
        else:
            content = "VERIFIED"
    else:
        content = "Generic"
        
    return {"choices": [{"message": {"content": content}}]}

def run1(): uvicorn.run(app1, host="127.0.0.1", port=8001, log_level="critical")
def run2(): uvicorn.run(app2, host="127.0.0.1", port=8002, log_level="critical")

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run1)
    p2 = multiprocessing.Process(target=run2)
    p1.start()
    p2.start()
    p1.join()
    p2.join()