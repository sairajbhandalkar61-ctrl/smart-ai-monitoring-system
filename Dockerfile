# ==============================================================================
# SENTINEL AI - Cloud Production Dockerfile
# Optimized for Railway, Render, or any Linux Cloud Container Service
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    IS_CLOUD=true \
    PORT=8501

WORKDIR /app

# Install system dependencies needed for PostgreSQL and compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install cloud Python dependencies
COPY requirements-cloud.txt /app/
RUN pip install --no-cache-dir -r requirements-cloud.txt

# Copy application source code
COPY sentinel/ /app/sentinel/
COPY server.py /app/
COPY app.py /app/
COPY scripts/ /app/scripts/
COPY docs/ /app/docs/

# Create data directory for SQLite fallback if Postgres is not attached
RUN mkdir -p /app/data && chmod -R 777 /app/data

# Expose Streamlit dashboard port and FastAPI port
EXPOSE 8000 8501

# Entrypoint script starts FastAPI in background and Streamlit in foreground
RUN chmod +x /app/scripts/docker_entrypoint.sh 2>/dev/null || true

CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true"]
