import requests

def seed_test_ordinance():
    url = "https://hosteva.onrender.com/api/ordinances/ingest"
    
    payload = {
        "jurisdiction": "Florida State (Sample)",
        "ordinance_text": "Sample Ordinance: All Short Term Rentals must register for a DBPR transient public lodging establishment license and remit both state sales tax and local county tourist development tax (TDT)."
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Successfully seeded test ordinance to production database.")
            print(response.json())
        else:
            print(f"Failed to seed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error during seeding: {str(e)}")

if __name__ == "__main__":
    seed_test_ordinance()
