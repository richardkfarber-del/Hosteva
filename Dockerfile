FROM python:3.12

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Application files
COPY . .
CMD ["gunicorn", "app:app"]
