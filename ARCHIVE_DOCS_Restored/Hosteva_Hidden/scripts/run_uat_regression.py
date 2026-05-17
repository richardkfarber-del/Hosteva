import urllib.request
import urllib.error
import urllib.parse
import json
import subprocess

BASE_URL = "https://hosteva.onrender.com"

def check_endpoint(path):
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except urllib.error.URLError:
        return False

def test_audit_api():
    url = f"{BASE_URL}/wizard/audit"
    data = json.dumps({"address": "123 Florida Ave"}).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_body = json.loads(response.read().decode('utf-8'))
                return response_body.get("status") == "Pass"
            return False
    except urllib.error.URLError:
        return False

def run_seed_script():
    try:
        result = subprocess.run(
            ["python3", "app/scripts/seed_florida_ordinances.py"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def main():
    endpoints = ["/", "/wizard", "/dashboard"]
    results = {}
    
    for endpoint in endpoints:
        results[endpoint] = check_endpoint(endpoint)
        
    audit_success = test_audit_api()
    seed_success = run_seed_script()
    
    print("## UAT Regression Report\n")
    
    for endpoint in endpoints:
        mark = "x" if results[endpoint] else " "
        print(f"- [{mark}] HTTP GET `{endpoint}` returned 200 OK")
        
    mark = "x" if audit_success else " "
    print(f"- [{mark}] HTTP POST `/wizard/audit` computed eligibility correctly")
        
    mark = "x" if seed_success else " "
    print(f"- [{mark}] Execute `app/scripts/seed_florida_ordinances.py` successfully")

if __name__ == "__main__":
    main()
