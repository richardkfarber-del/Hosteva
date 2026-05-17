# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies using uv
# We use the pyproject.toml to install dependencies but skip building the package
# to ensure static files and templates are preserved exactly as they are in the directory structure.
RUN pip install uv && uv pip install --system fastapi uvicorn gunicorn jinja2 pydantic pydantic-settings python-multipart python-jose[cryptography] passlib[bcrypt]

# Run the FastAPI server using Gunicorn and Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:10000", "app.main:app"]
