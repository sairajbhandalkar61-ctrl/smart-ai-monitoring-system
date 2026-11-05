#!/bin/sh
set -e

echo "=== SENTINEL AI Cloud Entrypoint Initializing ==="
echo "Binding FastAPI on port 8000..."
uvicorn server:app --host 0.0.0.0 --port 8000 &

echo "Binding Streamlit Command Center on port ${PORT:-8501}..."
exec streamlit run app.py --server.port "${PORT:-8501}" --server.address 0.0.0.0 --server.headless true
