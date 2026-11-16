# ScholarForge — container for Google Cloud Run
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

# Hosted defaults (override with --set-env-vars on deploy)
ENV PORT=8080 \
    AI_PROVIDER=huggingface \
    COOKIE_SECURE=true

# --proxy-headers: Cloud Run sits behind Google's proxy (real client IP in X-Forwarded-For)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips="*"
