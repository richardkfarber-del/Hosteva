FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies from pyproject.toml
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the source code over, excluding templates and static directories
COPY app/ .

# Ensure that the static files are copied correctly
COPY app/templates ./app/templates
COPY app/static ./app/static

# Set working directory
WORKDIR /app

# Expose port 10000
EXPOSE 10000

# Run the FastAPI server via Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:10000", "app.main:app"]
