# ── Stage 1: build dependencies ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime image ───────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application source and migration files
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# Factor 11: logs as event streams — unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

# Factor 7: port binding via $PORT env var
# Factor 9: fast startup / graceful shutdown via uvicorn signal handling
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
