import os
from dotenv import load_dotenv

print(f'Before load_dotenv: {os.environ.get("GEMINI_API_KEY")}')
load_dotenv()
print(f'After load_dotenv: {os.environ.get("GEMINI_API_KEY")}')
print(f'GOOGLE_API_KEY: {os.environ.get("GOOGLE_API_KEY")}')
