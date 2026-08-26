# Hosteva — Technical Specification (GTM Launch Strategy Phase)

# 1\. Architectural Overview & Technical Stack

Hosteva's GTM MVP is engineered with a modular, highly performant tech stack that prioritizes operational reliability, data consistency, and seamless integration with third-party billing and AI services:

- **Backend Web Framework:** FastAPI (Python 3.12) utilizing asynchronous endpoints to handle high-concurrency requests and webhooks.  
- **Database & ORM:** SQLAlchemy 2.0 with the async PostgreSQL driver in production, and SQLite for testing. Alembic handles database migrations.  
- **Asynchronous Task Worker:** Celery with Redis as a message broker to process long-running document audits and cron-based calendar updates.  
- **Billing & Monetization Gateway:** Stripe API (Stripe Checkout and webhooks) for subscription tiers and the $150 direct permit filing transactional fee.  
- **AI Processing Engine:** Google Gemini 1.5 Pro API via the Google GenAI SDK for OCR document verification, rule matching, and text extraction.  
- **Calendar Synchronization:** Asynchronous, standard iCal (`text/calendar` format) feed parsing to bypass external API partnership barriers on Airbnb and Vrbo.

---

# 2\. Database Schema Map

To support Stripe billing states, transactional add-on payments, and the simplified iCal synchronization engine, the schema is extended as follows:

\# app/models/gtm\_operations.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Text, DateTime, Float, func

from sqlalchemy.orm import declarative\_base, relationship

Base \= declarative\_base()

class Subscription(Base):

    \_\_tablename\_\_ \= 'subscriptions'

    

    id \= Column(Integer, primary\_key=True, autoincrement=True)

    host\_id \= Column(Integer, ForeignKey('hosts.id', ondelete='CASCADE'), nullable=False)

    stripe\_customer\_id \= Column(String(255), unique=True)

    stripe\_subscription\_id \= Column(String(255), unique=True)

    tier \= Column(String(100), default='FREE') \# 'FREE', 'STARTER', 'GROWTH', 'ENTERPRISE'

    status \= Column(String(100), default='INACTIVE') \# 'ACTIVE', 'PAST\_DUE', 'CANCELLED'

    created\_at \= Column(DateTime, default=func.now())

class PermitTransaction(Base):

    \_\_tablename\_\_ \= 'permit\_transactions'

    

    id \= Column(Integer, primary\_key=True, autoincrement=True)

    property\_id \= Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)

    stripe\_session\_id \= Column(String(255), unique=True)

    payment\_status \= Column(String(100), default='PENDING') \# 'PENDING', 'PAID', 'FAILED'

    amount\_paid \= Column(Float, default=150.0)

    created\_at \= Column(DateTime, default=func.now())

class Property(Base):

    \_\_tablename\_\_ \= 'properties'

    

    id \= Column(Integer, primary\_key=True, autoincrement=True)

    host\_id \= Column(Integer, ForeignKey('hosts.id'), nullable=False)

    title \= Column(String(255), nullable=False)

    address \= Column(String(500), nullable=False)

    property\_type \= Column(String(100))

    compliance\_score \= Column(Integer, default=0)

    

    \# Simple iCal feed URL mappings for OTA syncing (Airbnb, Vrbo fallbacks)

    airbnb\_ical\_import\_url \= Column(String(500))

    vrbo\_ical\_import\_url \= Column(String(500))

    hosteva\_ical\_export\_token \= Column(String(255), unique=True) \# Token to export Hosteva's unified block feed

class PropertyCompliance(Base):

    \_\_tablename\_\_ \= 'properties\_compliance'

    

    id \= Column(Integer, primary\_key=True, autoincrement=True)

    property\_id \= Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)

    municipal\_code\_id \= Column(Integer, ForeignKey('municipal\_codes.id'))

    task\_name \= Column(String(255), nullable=False) \# e.g. 'HOA Lease Review' or 'DBPR License'

    status \= Column(String(50), default='PENDING') \# 'PENDING', 'APPROVED', 'REJECTED'

    uploaded\_file\_url \= Column(String(500))

    ocr\_metadata\_json \= Column(Text) \# Extracted license numbers and dates

    verification\_notes \= Column(Text)

    created\_at \= Column(DateTime, default=func.now())

---

# 3\. Direct API Endpoints Specifications

### AI Document Auditor (OCR Audit)

* **`POST /api/v1/compliance/audit`**  
  - **Payload (Multipart Form-Data):** `property_compliance_id: int`, `file: UploadFile`  
  - **Action:** Saves the uploaded file to S3/local storage, updates `uploaded_file_url` in the database, transitions status to `PENDING`, and triggers background Celery task `tasks.process_document_ocr`.  
  - **Response (202):**  
      
    {  
      
      "property\_compliance\_id": 104,  
      
      "status": "PENDING",  
      
      "message": "File successfully uploaded. AI Document Auditor task enqueued."  
      
    }

### Simple iCal Synchronization (OTA Fallback)

* **`POST /api/v1/operations/sync-ical`**  
  - **Payload:**  
      
    {  
      
      "property\_id": 45,  
      
      "airbnb\_ical\_url": "https://www.airbnb.com/calendar/ical/12345.ics",  
      
      "vrbo\_ical\_url": "https://www.vrbo.com/calendar/ical/67890.ics"  
      
    }  
      
  - **Action:** Saves the incoming iCal URLs to the property's record and enqueues the Celery sync task `tasks.sync_ical_calendars`.  
  - **Response (200):**  
      
    {  
      
      "property\_id": 45,  
      
      "status": "SYNC\_QUEUED",  
      
      "message": "Calendar iCal import URLs registered. Synchronization in progress."  
      
    }

---

# 4\. Asynchronous Task Worker Specifications

### Task: `tasks.process_document_ocr`

- **Trigger:** Document upload to checklist item.  
- **Process Flow:**  
  1. Retrieve file binary and target compliance checklist task context.  
  2. Send the document (PDF or image) to Gemini 1.5 Pro alongside a system prompt indicating the required fields (e.g., license number, expiration date, name, and address checks).  
  3. Parse the JSON metadata returned by Gemini.  
  4. Compare the extracted address and owner name against the database. If they align, update the `PropertyCompliance` status to `APPROVED`. If a mismatch is found, update to `REJECTED` and serialize the error notes.

### Task: `tasks.sync_ical_calendars`

- **Trigger:** Cron schedule (every 60 minutes) or manual refresh.  
- **Process Flow:**  
  1. Download the latest `.ics` files from the property's registered `airbnb_ical_import_url` and `vrbo_ical_import_url`.  
  2. Parse the calendar events using a Python iCal parsing library (`icalendar`).  
  3. Extract blocked reservation date boundaries, update Hosteva's internal booking model, and export a unified, compiled `.ics` feed on a custom token-scoped endpoint to keep external channels in sync.

