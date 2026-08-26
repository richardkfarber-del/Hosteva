# Hosteva — Technical Specification (Phase III: Multi-State GTM & AI Agentic Launch)

# 1\. Architectural Overview & Technical Stack

Hosteva's GTM Expansion is engineered with a modular, highly performant tech stack that prioritizes operational reliability, data consistency, and seamless integration with third-party billing, AI services, and document generators:

- **Backend Web Framework:** FastAPI (Python 3.12) utilizing asynchronous endpoints to handle high-concurrency requests and webhooks.  
- **Database & ORM:** SQLAlchemy 2.0 with the async PostgreSQL driver in production, and SQLite for testing. Alembic handles database migrations.  
- **Asynchronous Task Worker:** Celery with Redis as a message broker to process long-running document audits and cron-based calendar updates.  
- **Billing & Monetization Gateway:** Stripe API (Stripe Checkout and webhooks) for subscription tiers and the $150 direct permit filing transactional fee.  
- **AI Processing Engine:** Google Gemini 1.5 Pro API via the Google GenAI SDK for OCR document verification, message response drafting, and scraping parsing.  
- **Web Scraping Infrastructure:** BeautifulSoup4 and `requests` / `httpx` (or Playwright/Puppeteer if JavaScript rendering is required) managed within isolated Celery worker tasks.  
- **PDF Manipulation Pipeline:** `PyPDF2` (for PDF field extraction and form filling) and `reportlab` (for overlaying field coordinates).

---

# 2\. Database Schema Map

To support 10-state coverage, AI-on-demand scraper metrics, expert review queues, and PDF application templates, the schema is extended as follows:

\# app/models/phase3\_operations.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Text, DateTime, Float, func

from sqlalchemy.orm import declarative\_base, relationship

Base \= declarative\_base()

class MunicipalCode(Base):

    \_\_tablename\_\_ \= 'municipal\_codes'

    

    id \= Column(Integer, primary\_key=True, autoincrement=True)

    state \= Column(String(50), nullable=False, index=True) \# e.g. 'FL', 'CA', 'TX'

    jurisdiction\_name \= Column(String(255), nullable=False, index=True)

    jurisdiction\_type \= Column(String(100), nullable=False) \# 'County' or 'City'

    str\_permitted \= Column(String(100), nullable=False)

    permit\_required \= Column(Boolean, default=False)

    minimum\_stay\_requirement \= Column(String(255))

    occupancy\_limits \= Column(String(255))

    tax\_rate\_registration\_fee \= Column(String(500))

    source\_url \= Column(String(500))

    

    \# AI-on-Demand Tracking Fields

    is\_ai\_scraped \= Column(Boolean, default=False) \# True if populated by background scraper

    is\_expert\_verified \= Column(Boolean, default=False) \# True if reviewed by admin team

    scraped\_at \= Column(DateTime)

    

    \# PDF Template Mapping

    form\_template\_path \= Column(String(500), nullable=True) \# S3 or local path to official permit PDF

class Property(Base):

    \_\_tablename\_\_ \= 'properties'

    

    id \= Column(String, primary\_key=True) \# UUID String

    host\_id \= Column(String, ForeignKey('hosts.id', ondelete='CASCADE'), nullable=False)

    title \= Column(String(255), nullable=False)

    address \= Column(String(500), nullable=False)

    city \= Column(String(255))

    county \= Column(String(255))

    state \= Column(String(50), index=True) \# 'FL', 'CA', 'TX', etc.

    zip\_code \= Column(String(50))

    compliance\_score \= Column(Integer, default=0)

class PropertyCompliance(Base):

    \_\_tablename\_\_ \= 'properties\_compliance'

    

    id \= Column(Integer, primary\_key=True, autoincrement=True)

    property\_id \= Column(String, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)

    municipal\_code\_id \= Column(Integer, ForeignKey('municipal\_codes.id'))

    task\_name \= Column(String(255), nullable=False) \# e.g. 'DBPR Vacation Rental License'

    status \= Column(String(50), default='NOT\_UPLOADED') \# 'NOT\_UPLOADED', 'PENDING', 'PENDING\_REVIEW', 'APPROVED', 'REJECTED'

    uploaded\_file\_url \= Column(String(500))

    ocr\_metadata\_json \= Column(Text)

    verification\_notes \= Column(Text)

---

# 3\. Direct API Endpoints Specifications

### AI-on-Demand Compliance Scraper Trigger

* **`POST /api/v1/compliance/agent/trigger`**  
  - **Payload:**  
      
    {  
      
      "property\_id": "prop-uuid-12345",  
      
      "city": "Key West",  
      
      "county": "Monroe County",  
      
      "state": "FL"  
      
    }  
      
  - **Action:** Triggers the Celery task `tasks.run_agent_compliance_scraper` if no pre-compiled database match is found. Instantly creates a temporary `MunicipalCode` record flagged with `is_ai_scraped = True` and `is_expert_verified = False`.  
  - **Response (202):**  
      
    {  
      
      "property\_id": "prop-uuid-12345",  
      
      "status": "SCRAPING\_ACTIVE",  
      
      "message": "Zoning rules not found in pre-compiled database. Initiating Real-time AI Scraper Agent."  
      
    }

### PDF Application Form Pre-filling

* **`POST /api/v1/compliance/tasks/{id}/fill-permit`**  
  - **Action:** Reads the compliance task's municipal code, checks if `form_template_path` is present, and triggers `tasks.generate_prefilled_permit_pdf` to overlay host data onto the form template.  
  - **Response (200):**  
      
    {  
      
      "download\_url": "https://hosteva-storage.s3.amazonaws.com/generated\_permits/prop\_45\_permit\_pkg.zip",  
      
      "status": "READY"  
      
    }

---

# 4\. Asynchronous Task Worker Specifications

### Task: `tasks.run_agent_compliance_scraper`

- **Trigger:** Cache-miss during property registration.  
- **Process Flow:**  
  1. Compile a web query target: `"[City Name] [State] short-term rental ordinance zoning rules permit"`.  
  2. Query search engines, filtering results to official domains (`.gov`, `.org`) or code aggregators (Municode, American Legal Publishing).  
  3. Download raw text/HTML pages, scrape content, and pass the combined text payload to Gemini 1.5 Pro.  
  4. System Prompt: Direct Gemini to parse the text into a structured JSON mapping our DB columns: `str_permitted`, `permit_required`, `minimum_stay_requirement`, `occupancy_limits`, `tax_rate_registration_fee`, `source_url`.  
  5. Save the parsed JSON to the `MunicipalCode` table with `is_ai_scraped = True`, update property compliance checklist tasks, and trigger a WebSocket push to update the user dashboard.

### Task: `tasks.generate_prefilled_permit_pdf`

- **Process Flow:**  
  1. Open the PDF template mapped to `form_template_path` using `PyPDF2`.  
  2. Extract form field names (`fields = reader.get_fields()`).  
  3. Query `Property` and `Host` tables to collect registration details.  
  4. Use FDF form-fill scripts or coordinate-based `reportlab` canvas layers to overlay details (e.g. host name, property address, county tax ID) onto form fields.  
  5. Package the pre-filled PDF and an instruction sheet into a `.zip` archive, upload it to storage, and return the secure download URL.

