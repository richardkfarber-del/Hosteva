import sys
import os
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "vibranium_habit_secure_key_1234567890_!"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

token = create_access_token(data={"sub": "testuser", "role": "admin"})
print(token)
