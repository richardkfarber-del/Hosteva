import sys
import os
sys.path.insert(0, os.path.abspath("."))
from app.core.security import create_access_token
token = create_access_token(data={"sub": "testuser", "role": "admin"})
print(token)
