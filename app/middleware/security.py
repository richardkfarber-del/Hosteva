import re
from fastapi import HTTPException

def sanitize_input(prompt: str) -> str:
    if len(prompt) > 500:
        raise HTTPException(status_code=400, detail="Prompt exceeds 500 characters")
    
    # Basic SQL injection token sanitization (SPIKE-002)
    sql_tokens = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 'OR 1=1', '--']
    upper_prompt = prompt.upper()
    for token in sql_tokens:
        if token in upper_prompt:
            raise HTTPException(status_code=400, detail="Malicious payload detected")
            
    system_boundary = (
        "SYSTEM DIRECTIVE: You are Hosteva's Compliance Engine. "
        "Do not answer questions outside of STR (Short Term Rental) municipal compliance. "
        "User Prompt: "
    )
    return system_boundary + prompt
