# Dockerfile for Ocean AI QA Framework (Render deployment)
# Uses a slim Python base, installs Chrome and ChromeDriver via webdriver-manager at runtime

FROM python:3.11-slim

# Prevent Python from writing pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       ca-certificates \
       wget \
       curl \
       gnupg \
       unzip \
       fonts-liberation \
       libnss3 \
       libxss1 \
       libasound2 \
       libatk1.0-0 \
       libatk-bridge2.0-0 \
       libx11-xcb1 \
       libxcb1 \
       libxcomposite1 \
       libxdamage1 \
       libxrandr2 \
       libgbm1 \
       libpangocairo-1.0-0 \
       # utilities
       procps \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (stable)
RUN wget -q -O /tmp/google-chrome-stable_current_amd64.deb \
      https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/google-chrome-stable_current_amd64.deb \
    && rm -rf /tmp/google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy dependency files first for better caching
COPY requirements.txt requirements-streamlit.txt requirements-ai.txt ./

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt -r requirements-streamlit.txt -r requirements-ai.txt \
    && pip install --no-cache-dir webdriver-manager

# Copy application code
COPY . /app

# Expose port (Render provides PORT env var during runtime)
EXPOSE 8502

# Environment defaults
ENV PORT=8502
ENV CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage --disable-gpu --single-process"
ENV PYTHONPATH=.

# Healthcheck (optional): try to hit the health endpoint
HEALTHCHECK --interval=1m --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Start the app using the existing render_start.py which spins up the HTTP server and background tasks
CMD ["python", "render_start.py"]
