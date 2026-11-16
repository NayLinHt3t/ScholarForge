# ScholarForge — container for Google Cloud Run (free-tier setup)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LOCAL_EMBED_MODEL=BAAI/bge-small-en-v1.5 \
    LOCAL_EMBED_CACHE=/srv/models

WORKDIR /srv
COPY requirements.txt requirements-cloud.txt ./
RUN pip install -r requirements-cloud.txt

# Download the embedding model once, at build time, so instances start without downloading.
RUN python -c "from fastembed import TextEmbedding; import os; TextEmbedding(os.environ['LOCAL_EMBED_MODEL'], cache_dir=os.environ['LOCAL_EMBED_CACHE'])"

COPY app ./app

# Run as a non-root user
RUN useradd --create-home appuser && chown -R appuser /srv/models
USER appuser

# Hosted defaults (override with --set-env-vars on deploy)
ENV PORT=8080 \
    AI_PROVIDER=groq \
    EMBED_PROVIDER=local \
    COOKIE_SECURE=true \
    HF_HUB_OFFLINE=1

# --proxy-headers: Cloud Run sits behind Google's proxy (real client IP in X-Forwarded-For)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips="*"
