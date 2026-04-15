import os
import sys
import json
import logging
import websocket

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_websocket():
    ws_url = "ws://127.0.0.1:18789"
    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")
    
    headers = []
    if token:
        headers.append(f"Authorization: Bearer {token}")
        
    payload = {
        "model": "agent:hawkeye",
        "messages": [{"role": "user", "content": "QA connection test."}],
        "stream": False
    }
    
    try:
        logger.info(f"Connecting to {ws_url}...")
        ws = websocket.create_connection(ws_url, header=headers, timeout=15)
        logger.info("Connected. Sending payload...")
        ws.send(json.dumps(payload))
        
        logger.info("Payload sent. Awaiting response...")
        message = ws.recv()
        logger.info(f"Received response: {message[:100]}...")
        ws.close()
        
        return True
    except Exception as e:
        logger.error(f"WebSocket test failed: {e}")
        return False

if __name__ == "__main__":
    if not test_websocket():
        sys.exit(1)
    sys.exit(0)
