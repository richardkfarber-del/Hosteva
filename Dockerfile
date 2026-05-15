FROM python:3.12

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Application files
COPY . .
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:10000", "app.main:app"]
