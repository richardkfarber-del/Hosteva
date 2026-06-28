import os
import json
import logging
import requests
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.tasks.config import celery_app
from app.database import SessionLocal
from app.models.compliance import MunicipalCode, PropertyCompliance
from app.models.property import Property
from app.db_models import QueueTask

logger = logging.getLogger(__name__)

class ScrapingException(Exception):
    pass

def call_gemini_parser(text_payload: str) -> dict:
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_AI_KEY")
        or os.getenv("GOOGLE_MAPS_API_KEY")
        or os.getenv("Maps_API_KEY")
    )
    if not api_key:
        raise ScrapingException("Gemini API key not configured in the environment.")

    prompt = f"""
    You are an AI zoning compliance parser. Extract short-term rental rules from the following scraped text payload.
    Ensure you return a valid JSON object matching our database columns.
    
    Database Columns to extract:
    - str_permitted: "Yes", "No", or "Restricted"
    - permit_required: true or false
    - minimum_stay_requirement: string description (e.g. "None", "30 nights minimum", etc.)
    - occupancy_limits: string description (e.g. "Max 2 per bedroom + 2", "Max 10 guests", etc.)
    - tax_rate_registration_fee: string description (e.g. "12% Transient tax, $150 BTR fee", etc.)
    - source_url: string URL citation

    Scraped Content payload:
    \"\"\"{text_payload[:8000]}\"\"\"

    Return a JSON object conforming exactly to this schema:
    {{
        "str_permitted": "Yes" | "No" | "Restricted",
        "permit_required": true | false,
        "minimum_stay_requirement": "Description string or None",
        "occupancy_limits": "Description string or None",
        "tax_rate_registration_fee": "Description string or None",
        "source_url": "URL string"
    }}
    
    Do not output any markdown formatting (like ```json), backticks, or prefix. Return raw JSON.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if resp.status_code == 200:
            result = resp.json()
            candidates = result.get("candidates", [])
            if candidates:
                content_part = candidates[0].get("content", {})
                parts = content_part.get("parts", [])
                if parts:
                    return json.loads(parts[0].get("text", "").strip())
        raise ScrapingException(f"Gemini API returned status code {resp.status_code}: {resp.text}")
    except Exception as e:
        raise ScrapingException(f"Gemini parsing failed: {e}")

@celery_app.task(name="tasks.run_agent_compliance_scraper")
def run_agent_compliance_scraper(property_id: str, city: str, county: str, state: str):
    logger.info(f"Initiating background scraper agent for property={property_id}, city={city}, county={county}, state={state}")
    
    db = SessionLocal()
    try:
        # Find temporary municipal code
        mc = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike(city),
            MunicipalCode.state.ilike(state)
        ).first()

        if not mc:
            raise ScrapingException(f"No temporary MunicipalCode record exists for {city}, {state}")

        # 1. Compile search query target
        search_query = f"{city} {state} short term rental ordinance zoning rules permit"
        encoded_query = urllib.parse.quote_plus(search_query)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # 2. Query search engines
        logger.info(f"Crawling search engine url={search_url}")
        resp = requests.get(search_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            raise ScrapingException(f"Search request failed with status code {resp.status_code}")
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find results links
        links = []
        for a in soup.find_all('a', class_='result__url'):
            href = a.get('href')
            if href:
                # Resolve DDG redirect URL if necessary
                if "uddg=" in href:
                    parsed = urllib.parse.urlparse(href)
                    queries = urllib.parse.parse_qs(parsed.query)
                    real_url = queries.get("uddg", [None])[0]
                    if real_url:
                        links.append(real_url)
                else:
                    links.append(href)
                    
        # Filter links prioritizing .gov, .org, municode
        target_links = [l for l in links if ".gov" in l or ".org" in l or "municode" in l]
        if not target_links:
            target_links = links[:3]
            
        if not target_links:
            raise ScrapingException("Search yielded no crawlable result links.")
            
        # 3. Crawl target pages and extract text
        scraped_text = ""
        crawled_url = target_links[0]
        logger.info(f"Crawling top candidate link={crawled_url}")
        
        page_resp = requests.get(crawled_url, headers=headers, timeout=15)
        if page_resp.status_code == 200:
            page_soup = BeautifulSoup(page_resp.text, 'html.parser')
            # Extract main text
            for script in page_soup(["script", "style"]):
                script.decompose()
            scraped_text = page_soup.get_text(separator=" ")
            scraped_text = " ".join(scraped_text.split())
        else:
            raise ScrapingException(f"Crawl failed for target page {crawled_url} with status {page_resp.status_code}")
            
        if not scraped_text or len(scraped_text) < 100:
            raise ScrapingException("Extracted scraped text is empty or too short.")
            
        # 4. Parse with Gemini
        logger.info("Sending payload to Gemini for zoning extraction...")
        extracted = call_gemini_parser(scraped_text)
        
        # Validate extracted fields
        str_permitted = extracted.get("str_permitted") or "Restricted"
        permit_required = bool(extracted.get("permit_required"))
        min_stay = extracted.get("minimum_stay_requirement")
        occ_limits = extracted.get("occupancy_limits")
        tax_fees = extracted.get("tax_rate_registration_fee")
        source_url = extracted.get("source_url") or crawled_url
        
        # 5. Save parsed JSON to MunicipalCode
        mc.str_prohibited = (str_permitted == "No")
        mc.is_allowed = (str_permitted != "No")
        mc.requires_permit = permit_required
        mc.minimum_stay_requirement = min_stay
        mc.occupancy_limits = occ_limits
        mc.tax_rate_registration_fee = tax_fees
        mc.source_url = source_url
        mc.is_ai_scraped = True
        mc.is_expert_verified = False
        mc.scraped_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Successfully saved AI scraped rules for {city}, {state}")
        
        # 6. Generate property compliance tasks based on scraped permit requirements
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if property_obj:
            valid_period = '[2026-06-04 00:00:00, 2027-06-04 00:00:00]'
            
            # Determine checklist task name
            if permit_required:
                task_name = f"{city} Short-Term Rental Permit"
                
                # Check if compliance task already exists
                exists = db.query(PropertyCompliance).filter(
                    PropertyCompliance.property_id == property_id,
                    PropertyCompliance.task_name == task_name
                ).first()
                
                if not exists:
                    new_task = PropertyCompliance(
                        property_id=property_id,
                        municipal_code_id=mc.id,
                        is_compliant=False,
                        status="NOT_UPLOADED",
                        task_name=task_name,
                        violation_notes=task_name,
                        valid_period=valid_period
                    )
                    db.add(new_task)
                    
            # Add state specific tax tasks if transient occupancy tax is mentioned
            if tax_fees and "tax" in tax_fees.lower():
                tax_task = f"{state} Transient Occupancy Tax Registration"
                exists_tax = db.query(PropertyCompliance).filter(
                    PropertyCompliance.property_id == property_id,
                    PropertyCompliance.task_name == tax_task
                ).first()
                
                if not exists_tax:
                    new_tax_task = PropertyCompliance(
                        property_id=property_id,
                        municipal_code_id=mc.id,
                        is_compliant=False,
                        status="NOT_UPLOADED",
                        task_name=tax_task,
                        violation_notes=tax_task,
                        valid_period=valid_period
                    )
                    db.add(new_tax_task)
            
            # Update property zoning status based on STR permission rules
            property_obj.zoning_status = "Compliant" if str_permitted != "No" else "Violation"
            
            db.commit()
            
    except Exception as e:
        logger.error(f"Scraper task failed: {e}. Enqueuing expert manual review queue task.")
        db.rollback()
        
        # Enqueue manual curation task in queue_tasks
        curation_task = QueueTask(
            task_name="expert_curation",
            payload=json.dumps({
                "property_id": property_id,
                "city": city,
                "county": county,
                "state": state,
                "reason": f"AI Web Crawler/Gemini extraction failure: {str(e)}"
            }),
            status="pending"
        )
        db.add(curation_task)
        
        # Set property zoning status to Manual Review fallback
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if property_obj:
            property_obj.zoning_status = "Rules Under Manual Review"
            
            # Also create a manual compliance check task for the property detail list
            mc = db.query(MunicipalCode).filter(
                MunicipalCode.municipality_name.ilike(city),
                MunicipalCode.state.ilike(state)
            ).first()
            if mc:
                task_name = "Zoning Rules Under Manual Curation"
                exists = db.query(PropertyCompliance).filter(
                    PropertyCompliance.property_id == property_id,
                    PropertyCompliance.task_name == task_name
                ).first()
                if not exists:
                    valid_period = '[2026-06-04 00:00:00, 2027-06-04 00:00:00]'
                    new_task = PropertyCompliance(
                        property_id=property_id,
                        municipal_code_id=mc.id,
                        is_compliant=False,
                        status="PENDING_REVIEW",  # Triggers Rules Under Manual Review indicator
                        task_name=task_name,
                        violation_notes="System enqueued for manual curator review.",
                        valid_period=valid_period
                    )
                    db.add(new_task)
                    
        db.commit()
        # Re-raise the exception so Celery marks it as failed
        raise e
    finally:
        db.close()
