import os
import json
import requests
import base64

def run_gemini_audit(city: str, county: str, state: str, address: str, address_components: list = None) -> dict:
    """
    Calls the Gemini API to analyze short-term rental regulations, zoning ordinances,
    and HOA presence / CC&Rs for the specific address and jurisdiction.
    Returns a dictionary with: legal_subdivision_name, hoa_detected, hoa_rules_available,
    eligibility_status, required_permits, and local_restrictions.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_AI_KEY")
    
    print(f"Gemini Compliance Engine: Auditing address='{address}', city='{city}', county='{county}', state='{state}'")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in the environment.")

    prompt = f"""
    You are an expert zoning analyst and short-term rental compliance officer.
    Perform an aggressive Forensic HOA and zoning compliance audit on the following property:
    Address: {address}
    City: {city}
    County: {county}
    State: {state}
    Geocoding Components: {json.dumps(address_components) if address_components else '[]'}
    
    Your goals:
    1. Extract the Legal Subdivision Name of the property from the address and geocoding components (e.g. identifying developments like 'Lone Star Townhomes', 'Sunset Valley', 'Oak Ridge', or similar for Spring Hill or other addresses). If no subdivision can be extracted, provide a name representing the immediate neighborhood or development.
    2. Audit CC&Rs: Specifically cross-reference the identified subdivision name against the Florida Secretary of State (Sunbiz) and County Clerk Official Records for recorded HOA presence or CC&R covenants.
    3. Prioritize Rent Covenants: Search for any lease covenants, minimum stay rules, or lease frequency regulations (e.g., minimum of 3 months lease, sub-leasing bans, occupancy limits).
    4. Determine the HOA status:
       - Set "hoa_detected" to true if an HOA/CC&R presence is found or highly suspected.
       - Set "hoa_rules_available" to true if public HOA rules/restrictions/CC&Rs are found.
       - If public rules are found, summarize the specific STR restrictions under local_restrictions (specifically mentioning 'Minimum Stay' or 'Lease Duration' limits). If rules prohibit standard daily STR (e.g. demanding a 3-month minimum duration), set "eligibility_status" to "Violation".
       - Only if an HOA/CC&R presence is suspected/confirmed but a deep search yields zero rules/documents, set "hoa_rules_available" to false, "eligibility_status" to "Action Required", and add the exact task: "HOA Detected: Public rules unavailable. Please upload governing documents for AI scanning." to the "required_permits" array.
       - If no HOA/CC&Rs exist at all, analyze standard zoning and set "eligibility_status" to "Compliant" or "Violation".
    
    Return a JSON object conforming exactly to this schema:
    {{
        "legal_subdivision_name": "Name of Legal Subdivision",
        "hoa_detected": true | false,
        "hoa_rules_available": true | false,
        "eligibility_status": "Compliant" | "Violation" | "Pending" | "Action Required",
        "required_permits": ["Name of Permit A", "Name of Permit B", ...],
        "local_restrictions": {{
            "Noise": "Details of quiet hours or noise limits",
            "Parking": "Details of parking spaces or vehicle limits",
            "Trash": "Details of trash collection schedules and bin storage rules",
            "HOA Rules": "Summary of HOA lease / STR restrictions (if rules found)"
        }}
    }}
    
    Do not output any markdown formatting (like ```json), backticks, or prefix. Return raw JSON conforming exactly to this schema.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    print("Gemini Compliance Engine: Direct API request sent to generativelanguage.googleapis.com...")
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    print(f"Gemini Compliance Engine API response status code: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        text_response = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Handle potential JSON parsing or cleanup
        if text_response.startswith("```json"):
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif text_response.startswith("```"):
            text_response = text_response.split("```")[1].split("```")[0].strip()
        
        parsed_data = json.loads(text_response)
        
        # Post-process to ensure Action Required is set if rules are unavailable
        if parsed_data.get("hoa_detected") and not parsed_data.get("hoa_rules_available"):
            parsed_data["eligibility_status"] = "Action Required"
            task_msg = "HOA Detected: Public rules unavailable. Please upload governing documents for AI scanning."
            if task_msg not in parsed_data.get("required_permits", []):
                parsed_data.setdefault("required_permits", []).append(task_msg)
        
        print("Gemini Compliance Engine: Successfully received and parsed AI compliance audit.")
        return parsed_data
    else:
        raise RuntimeError(f"Gemini API returned error response (status code {resp.status_code}): {resp.text}")


def run_gemini_vision(image_bytes: bytes, mime_type: str) -> dict:
    """
    Calls the Gemini 1.5 Pro Vision model to analyze a short-term rental property photo.
    Detects room type and features like pool, hot tub, stove/oven, and estimated bedrooms.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_AI_KEY")
    
    # Prompt requested by user with minor addition for standard features
    prompt = "Analyze this photo of a short-term rental property. Return a JSON object identifying the room_type (e.g., Kitchen, Backyard, Bedroom, Living Room) and the presence (true/false) features that should be called out in a short term rental listing. Do not include markdown formatting."
    
    print("Gemini Vision Engine: Running photo analysis...")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in the environment.")

    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": base64_image
                    }
                }
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    print("Gemini Vision Engine: Direct API request sent to generativelanguage.googleapis.com...")
    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    print(f"Gemini Vision Engine API response status code: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        text_response = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Handle potential JSON formatting
        if text_response.startswith("```json"):
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif text_response.startswith("```"):
            text_response = text_response.split("```")[1].split("```")[0].strip()
            
        parsed = json.loads(text_response)
        print(f"Gemini Vision Engine Result: {parsed}")
        return parsed
    else:
        raise RuntimeError(f"Gemini API returned error response (status code {resp.status_code}): {resp.text}")

