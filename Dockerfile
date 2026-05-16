FROM python:3.12

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv pip install --system .

# Application files
COPY . .
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:10000", "app.main:app"]
