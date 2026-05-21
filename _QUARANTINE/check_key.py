import os
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get('GOOGLE_API_KEY', '')
print(f'Key length: {len(key)}')
print(f'Starts with AIza: {key.startswith("AIza")}')
print(f'Has whitespace: {any(c.isspace() for c in key)}')
print(f'Ends with newline or carriage return: {key.endswith(chr(10)) or key.endswith(chr(13))}')
