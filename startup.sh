echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

echo "Starting Streamlit..."
streamlit run health.py --server.port $PORT --server.address 0.0.0.0
