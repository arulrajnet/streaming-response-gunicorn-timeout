FROM python:3.11.9-slim-bookworm

LABEL maintainer="Arul <arul@example.com>"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential

COPY app.py gunicorn_config.py ./
COPY templates ./templates

ENV PORT=5001 \
    GUNICORN_WORKERS=2

EXPOSE 5001

CMD ["gunicorn", "-c", "/app/gunicorn_config.py", "app:app"]
