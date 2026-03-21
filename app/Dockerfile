# ── Stage: build ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="Estudiante Maestría"
LABEL description="API Login con bcrypt + JWT + Gmail SMTP"
LABEL version="2.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Instalar dependencias del sistema (necesarias para bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Usuario no-root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
