# SPIKE-018: Blueprint for Replacing `pip` with `uv` in FastAPI Dockerfiles

## Objective
Migrate from standard `pip` and `requirements.txt` to Astral's `uv` package manager using `pyproject.toml` and `uv.lock` in our FastAPI application Dockerfiles. The goal is to achieve sub-50MB Docker layers, drastically reduce CI/CD build times, implement proper BuildKit caching, guarantee deterministic dependency resolution, and establish a hardened, non-root runtime environment.

---

## 1. The Strategy: Multi-Stage Build with `uv`

`uv` is an extremely fast Python package installer and resolver written in Rust. By utilizing its native project management capabilities (`uv sync`) alongside BuildKit cache mounts, we eliminate pip cache bloat and achieve mathematical reproducibility for our dependency graphs.

### Final vs. Builder Layers
We will split the Dockerfile into two stages:
1.  **Builder Stage**: Ingests `pyproject.toml` and `uv.lock`, mounts BuildKit caches, and builds a pristine virtual environment using `uv sync --frozen`.
2.  **Final Stage**: A minimal, secure runtime environment that executes strictly as a non-root user (`hosteva_user`), inheriting only the compiled virtual environment and application source.

---

## 2. Dockerfile Implementation Blueprint

Replace the existing FastAPI Dockerfile with the following structure:

```dockerfile
# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

# 1. Pull the pre-compiled uv binary from Astral's official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Set uv configurations
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# 3. Create a virtual environment and set it in the PATH
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 4. Install dependencies using BuildKit Cache Mounts & Native UV Project Management
# We bind-mount pyproject.toml and uv.lock to guarantee reproducibility without layer bloat
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# ==========================================
# Stage 2: Final Runtime
# ==========================================
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# 1. Create a non-root user for security compliance (Render/Docker best practices)
RUN useradd -m -u 1000 hosteva_user

WORKDIR /app

# 2. Copy the compiled virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

# 3. Copy the application source code and adjust ownership
COPY --chown=hosteva_user:hosteva_user . /app

# 4. Drop privileges to the non-root user
USER hosteva_user

# 5. Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3. Architecture Evaluation: Render & Docker Viability

This architectural upgrade perfectly aligns with Hosteva's infrastructure:
1.  **Non-Root Execution (`hosteva_user`)**: Adheres to the principle of least privilege. In cloud-native environments like Render, running web services as a non-root user is a critical security hardening step that prevents container breakout vulnerabilities.
2.  **`pyproject.toml` & `uv.lock`**: Moving away from legacy `requirements.txt` embraces modern Python standards (PEP 518/621). The `uv.lock` file guarantees mathematical reproducibility across the Swarm, ensuring that what passes locally on WSL2 is byte-for-byte identical to the production build on Render.

---

## 4. WSL2 Pathing & Environment Considerations

Because Hosteva runs on native Linux via Windows 11 WSL2, the following constraints must be respected:

1.  **Line Endings (CRLF vs LF)**:
    If developers use Windows IDEs, files might get saved with `CRLF`. This causes Docker execution failures (e.g., `\r: command not found`). 
    *   **Fix**: Enforce `text eol=lf` in `.gitattributes` for all `.txt`, `.toml`, `.lock`, `.sh`, and `Dockerfile` files.
2.  **Volume Mounts & File Watching**:
    When running in development via Docker Compose, mounting the host directory into `/app` will mask the container's `/app`. 
    *   **Fix**: Always explicitly exclude the virtual environment from the mount. If using a bind mount, do not map the host's `.venv` to the container, as Windows/WSL2 compiled binaries are incompatible with the container's Linux environment. Use an anonymous volume for `/opt/venv` if doing live local development.
3.  **File System Performance**:
    WSL2 suffers heavy performance penalties when Docker crosses the OS boundary (e.g., mounting `/mnt/c/...`). 
    *   **Fix**: Keep the project files within the WSL2 filesystem (`/home/rdogen/...`), which is already the case. BuildKit's `/root/.cache/uv` mount operates entirely within the Docker engine's VHD, completely avoiding WSL2 IO bottlenecks.

---

## 5. Why this Achieves Sub-50MB Layers

1.  **No Package Manager Bloat**: `pip`, `setuptools`, and `wheel` build dependencies are left behind in the `builder` stage.
2.  **No Source Archives**: The `--mount=type=cache` flag ensures that downloaded archives are stored in Docker's builder cache, *not* in the image layers.
3.  **Bytecode Pre-compiled**: `UV_COMPILE_BYTECODE=1` strips out source parsing overhead at runtime.
4.  **No Transient Bind Layers**: Using `--mount=type=bind` for `pyproject.toml` and `uv.lock` means the project files don't consume kilobyte traces in the builder image history.

---

## Next Steps for QA
1.  Verify the multi-stage build locally using `docker build --no-cache .` vs `docker build .` to validate the `uv` cache hit.
2.  Use `docker history <image_name>` to audit layer sizes and confirm the virtual environment layer is well under the 50MB threshold.
