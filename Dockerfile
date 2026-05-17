FROM python:3.12

# Copy all files first so the package can be built
COPY . .

# Install uv and dependencies
RUN pip install uv && uv pip install --system .

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:10000", "app.main:app"]
