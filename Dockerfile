FROM python:3.12-slim

WORKDIR /workspace

# Install uv
RUN pip install uv

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install all dependencies into the system environment
RUN uv pip install --system .

# CRITICAL: Copy the actual application files AFTER installing dependencies
# This ensures app/templates/ and app/static/ are not dropped by the package build.
COPY app/ /workspace/app/

# Run the FastAPI server via Gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT"]
