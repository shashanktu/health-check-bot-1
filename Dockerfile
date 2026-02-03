# # Multi-stage Dockerfile for Smoke Test Bot with Streamlit and Playwright

# # Build stage
# FROM python:3.11-slim as builder

# WORKDIR /build

# # Install build dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Install Node.js for Playwright
# RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
#     && apt-get install -y nodejs

# # Copy requirements and install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir --user -r requirements.txt

# # Install Playwright browsers
# RUN /root/.local/bin/playwright install chromium
# RUN /root/.local/bin/playwright install-deps chromium

# # Runtime stage
# FROM python:3.11-slim

# WORKDIR /app

# # Install runtime dependencies including Node.js
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     ca-certificates \
#     && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
#     && apt-get install -y nodejs \
#     && rm -rf /var/lib/apt/lists/*

# # Copy Python dependencies and Playwright from builder
# COPY --from=builder /root/.local /root/.local
# COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# # Copy application code
# COPY . .

# # Create startup script
# RUN echo '#!/bin/bash\n\
# set -e\n\
# echo "Starting FastAPI on port 8000..."\n\
# uvicorn app.main:app --host 0.0.0.0 --port 8000 &\n\
# echo "Starting Streamlit on port 8501..."\n\
# streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0 &\n\
# wait' > /app/start.sh && chmod +x /app/start.sh

# # Set environment variables
# ENV PATH=/root/.local/bin:$PATH \
#     PYTHONUNBUFFERED=1 \
#     DEBUG=false \
#     LOG_LEVEL=INFO \
#     PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# # Expose ports
# EXPOSE 8000 8501

# # Run both applications
# CMD ["/app/start.sh"]
# --------------------
# Base image: Python 3.11
# --------------------
FROM python:3.11-slim

# Avoid interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# --------------------
# Install Node.js + system dependencies
# --------------------
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# --------------------
# Install Playwright + Browsers
# --------------------
RUN npm install -g playwright @playwright/test \
    && playwright install \
    && playwright install-deps

# --------------------
# Copy Python dependencies
# --------------------
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# --------------------
# Copy app code
# --------------------
COPY . .

# --------------------
# Install local Playwright dependencies
# --------------------
RUN npm init -y && npm install @playwright/test

# --------------------
# Install Supervisor (to run 2 commands together)
# --------------------
RUN apt-get update && apt-get install -y supervisor

# --------------------
# Add supervisor config file
# --------------------
RUN mkdir -p /etc/supervisor/conf.d

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# --------------------
# Expose ports
# --------------------
# FastAPI port
EXPOSE 8000
# Streamlit port
EXPOSE 8501

# --------------------
# Start Supervisor
# --------------------
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
