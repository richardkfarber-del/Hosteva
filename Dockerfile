FROM python:3.12-slim
WORKDIR /app/workspace/Hosteva
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn "python-jose[cryptography]" passlib bcrypt
COPY . .
EXPOSE 8000
CMD gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}
