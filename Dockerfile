FROM python:3.12-slim

WORKDIR /workspace

# Install uv
RUN pip install uv

# Copy dependency definition files
COPY requirements.txt ./

# Install all dependencies into the system environment
RUN uv pip install --system -r requirements.txt

# CRITICAL: Copy the actual application files AFTER installing dependencies
# This ensures app/templates/ and app/static/ are not dropped by the package build.
COPY app/ /workspace/app/
COPY README.md /workspace/
COPY init_db.py /workspace/

# Run database initialization and then the FastAPI server via Gunicorn
CMD ["sh", "-c", "python init_db.py && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"]
