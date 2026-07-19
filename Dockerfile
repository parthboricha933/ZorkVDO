# ZorkVDO backend Dockerfile (at repo root for Railway compatibility)
# Build context: repo root
#
# NOTE: Heavy CV packages (ultralytics, mediapipe, easyocr) are NOT installed
# in the Docker image to keep build time under 5 minutes and avoid OOM.
# They're installed on first run via a startup script. The backend degrades
# gracefully without them (falls back to OpenCV Haar for faces, skips
# OCR/pose/object detection).
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for OpenCV + ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake ffmpeg libgl1 libglib2.0-0 libsm6 libxext6 \
    libxrender1 libjpeg-dev zlib1g-dev libpng-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages (no heavy CV extras)
COPY zorkvdo/packages/shared_schemas /app/packages/shared_schemas
COPY zorkvdo/packages/ai_engine /app/packages/ai_engine
RUN pip install /app/packages/shared_schemas /app/packages/ai_engine

COPY zorkvdo/services/backend/pyproject.toml zorkvdo/services/backend/README.md /app/services/backend/
WORKDIR /app/services/backend
RUN pip install --upgrade pip && pip install -e .

# ── Runtime stage ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libgl1 libglib2.0-0 libsm6 libxext6 \
    libxrender1 libjpeg-dev zlib1g-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY zorkvdo/packages /app/packages
COPY zorkvdo/services/backend /app/services/backend

WORKDIR /app/services/backend

ENV APP_ENV=production \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    PYTHONPATH=/app/services/backend:/app/packages/shared_schemas:/app/packages/ai_engine \
    DEMO_MODE=false

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
    CMD curl -fsS http://localhost:${PORT:-8000}/api/v1/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
