#!/bin/bash

echo "Installing nginx..."
apt-get update
apt-get install -y nginx

echo "Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

echo "Starting Streamlit..."
streamlit run health.py --server.port 8501 --server.address 0.0.0.0 &

echo "Starting nginx..."
nginx -c $(pwd)/nginx.conf -g "daemon off;"
