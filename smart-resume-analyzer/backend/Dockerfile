# ──────────────────────────────────────────────────────────────
# Smart Resume Analyzer — Backend Dockerfile (single-stage)
# ──────────────────────────────────────────────────────────────

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build + runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into /usr/local (accessible by all users)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model via direct versioned URL
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Create non-root user
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid appuser --shell /bin/bash --create-home appuser

# Copy application code
COPY . .

# Create uploads directory with correct permissions
RUN mkdir -p /app/uploads && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
