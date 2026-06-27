import os
import requests
import json
import logging
from sqlalchemy.orm import Session

from app.tasks.config import celery_app
from app.database import SessionLocal
from app.db_models import GuestMessage

def call_gemini_suggested_reply(message_text: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback to local draft generator
        return f"Hi! Thank you for your message. We have received it and will look into it shortly. Best, Host."
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        prompt = (
            f"You are an assistant for a short-term rental host. The guest has sent the following message:\n"
            f"\" {message_text} \"\n\n"
            f"Please draft a professional, polite, and helpful response to this guest. Keep it friendly and concise."
        )
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if resp.status_code == 200:
            raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return raw_text.strip()
    except Exception as e:
        logging.error(f"Gemini suggested reply generation failed: {e}")
        
    return f"Hi! Thank you for reaching out. We appreciate your message and will get back to you soon."

@celery_app.task(name="app.tasks.generate_ai_suggested_reply")
def generate_ai_suggested_reply(message_id: int):
    logging.info(f"Starting generate_ai_suggested_reply for message_id={message_id}")
    
    db: Session = SessionLocal()
    try:
        # 1. Fetch message
        msg = db.query(GuestMessage).filter(GuestMessage.id == message_id).first()
        if not msg:
            logging.error(f"Guest message {message_id} not found.")
            return False
            
        # 2. Call Gemini
        suggested_reply = call_gemini_suggested_reply(msg.message_text)
        
        # 3. Save reply
        msg.ai_suggested_reply = suggested_reply
        db.commit()
        logging.info(f"Suggested reply saved successfully for message {message_id}")
        return True
    except Exception as e:
        logging.error(f"Error in generate_ai_suggested_reply: {e}")
        try:
            db.rollback()
        except:
            pass
        return False
    finally:
        db.close()
