# syntax=docker/dockerfile:1

# ---- builder: build the application + dependency wheels (build tools stay out of runtime) ----
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Build a wheel for the gateway package and all of its runtime dependencies.
COPY pyproject.toml ./
COPY app ./app
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

# ---- runtime: slim image, no build tools, non-root user (capstone §7) ----
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Patch the base image's bundled pip/setuptools/wheel (CVE fixes for the
# build-tooling metadata Trivy flags even though the app never imports them).
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Non-privileged user (UID 10001) — the container must never run as root.
RUN groupadd --system --gid 10001 appuser \
    && useradd --system --uid 10001 --gid appuser --no-create-home appuser

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels terraform-review-api \
    && rm -rf /wheels

COPY app ./app

# Local SQLite/data dir (AKS uses Azure SQL); owned by the non-root user.
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
