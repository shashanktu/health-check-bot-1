#!/bin/bash

# start FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# start Streamlit
streamlit run health.py --server.port 8501 --server.address 0.0.0.0 &

# start nginx
nginx -c $(pwd)/nginx.conf -g "daemon off;"
