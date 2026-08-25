# Hosteva — Environment Variables Blueprint (GTM Launch Strategy Phase)

# Save this file as 'ops/.env' in your repository root and configure local values

# \--- Server Settings \---

HOST=0.0.0.0 PORT=8000 ENVIRONMENT=production

# \--- Relational Database \---

# For PostgreSQL Production deployment with pgvector

DATABASE\_URL=postgresql+psycopg://postgres:your\_secure\_password@localhost:5432/hosteva\_prod

# For local SQLite development

# DATABASE\_URL=sqlite:///./hosteva.db

# \--- Background Worker Queue (Redis) \---

REDIS\_URL=redis://localhost:6379/0

# \--- Core AI Engine Config (Google Gemini) \---

GEMINI\_API\_KEY=your\_google\_gemini\_api\_key\_here

# \--- Geocoding & Street View (Google Maps Platform) \---

GOOGLE\_MAPS\_API\_KEY=your\_google\_maps\_api\_key\_here

# \--- Payment Gateway (Stripe Subscription & Transaction Add-ons) \---

STRIPE\_API\_KEY=your\_stripe\_api\_key\_here STRIPE\_WEBHOOK\_SECRET=your\_stripe\_webhook\_secret\_here

# \--- Email Alert Dispatcher (SMTP Config) \---

SMTP\_SERVER=smtp.gmail.com SMTP\_PORT=587 SMTP\_USERNAME=[notifications@hosteva.com](mailto:notifications@hosteva.com) SMTP\_PASSWORD=your\_smtp\_app\_password\_here

# \--- Session Security \---

JWT\_SECRET\_KEY=your\_super\_secret\_jwt\_hmac\_key\_here JWT\_ALGORITHM=HS256 ACCESS\_TOKEN\_EXPIRE\_MINUTES=1440  
