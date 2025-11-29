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

    # Install Chrome based on architecture
    RUN if [ "$(uname -m)" = "x86_64" ]; then \
        # AMD64 architecture
        wget -q -O /tmp/google-chrome-stable_current_amd64.deb \
            https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
        && apt-get update \
        && apt-get install -y --no-install-recommends /tmp/google-chrome-stable_current_amd64.deb \
        && rm -rf /tmp/google-chrome-stable_current_amd64.deb; \
    else \
        # ARM64 or other architectures - use Chromium
        echo "Installing Chromium for non-AMD64 architecture" \
        && apt-get update \
        && apt-get install -y --no-install-recommends chromium chromium-driver; \
    fi \
    && rm -rf /var/lib/apt/lists/*# Create app directory
WORKDIR /app

# Copy dependency files first for better caching
COPY requirements-render.txt ./

# Upgrade pip and install Python dependencies with error handling
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --only-binary=all -r requirements-render.txt \
    || (echo "Installing with fallback options..." && pip install --no-cache-dir -r requirements-render.txt --no-build-isolation) \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY . /app

# Expose port (Render provides PORT env var during runtime)
EXPOSE 8501

# Environment defaults for Streamlit
ENV PORT=8501
ENV CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage --disable-gpu --single-process"
ENV PYTHONPATH=.
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Healthcheck for Streamlit
HEALTHCHECK --interval=1m --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# Start the Streamlit app via production script
CMD ["python", "production_start.py"]
