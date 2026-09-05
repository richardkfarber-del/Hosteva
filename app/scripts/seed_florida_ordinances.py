import os
import requests

def seed_test_ordinance():
    """TE-005: Sample ordinances must never be pushed to production."""
    if os.getenv("ENVIRONMENT", "").lower() == "production":
        raise SystemExit("Refusing to seed sample ordinances when ENVIRONMENT=production")

    # Local/dev only — do not target live Render by default
    base = os.getenv("HOSTEVA_SEED_BASE_URL", "http://127.0.0.1:8000")
    url = f"{base.rstrip('/')}/api/ordinances/ingest"

    payload = {
        "jurisdiction": "Florida State (Sample)",
        "ordinance_text": "DEV FIXTURE ONLY — Sample Ordinance for non-production tests."
    }

    response = requests.post(url, json=payload, timeout=30)
    print(response.status_code, response.text)

if __name__ == "__main__":
    seed_test_ordinance()
