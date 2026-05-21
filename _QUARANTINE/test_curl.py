import os
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get('GOOGLE_API_KEY', '')

url = f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'

try:
    with urllib.request.urlopen(url) as response:
        print(f'Status Code: {response.status}')
        print(f'Response: {response.read().decode("utf-8")[:100]}...')
except urllib.error.HTTPError as e:
    print(f'Status Code: {e.code}')
    print(f'Response: {e.read().decode("utf-8")}')
