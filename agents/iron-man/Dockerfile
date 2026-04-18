FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure psycopg[binary] v3 is installed per Database Driver Rule
RUN pip install --no-cache-dir "psycopg[binary]" gunicorn uvicorn

COPY . .

# Render Port Binding Rule: Never hardcode EXPOSE 8000 in the Dockerfile.
# Use CMD gunicorn ... --bind 0.0.0.0:${PORT:-8000}
CMD ["sh", "-c", "gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}"]
