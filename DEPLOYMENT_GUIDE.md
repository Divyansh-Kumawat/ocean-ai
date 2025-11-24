# 🚀 Deployment Guide - E-Shop Checkout QA Framework

This comprehensive guide provides step-by-step instructions for deploying the E-Shop Checkout QA Testing Framework in various environments.

## 📋 Table of Contents

1. [Quick Deployment (Local)](#quick-deployment-local)
2. [Production Server Deployment](#production-server-deployment)
3. [Docker Deployment](#docker-deployment)
4. [CI/CD Pipeline Integration](#cicd-pipeline-integration)
5. [Cloud Deployment (AWS/Azure/GCP)](#cloud-deployment)
6. [Troubleshooting](#troubleshooting)

---

## 🏃‍♂️ Quick Deployment (Local)

### Prerequisites
- **Python 3.8+** installed
- **Chrome browser** installed
- **Git** installed
- **Internet connection** for ChromeDriver download

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/Divyansh-Kumawat/ocean-ai.git
cd ocean-ai

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for ChromeDriver auto-management
pip install webdriver-manager
```

### Step 2: Verify Installation
```bash
# Test Python dependencies
python3 -c "import selenium, pytest; print('✅ Dependencies installed successfully')"

# Test ChromeDriver access
python3 -c "
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.quit()
print('✅ ChromeDriver working correctly')
"
```

### Step 3: Start Local Web Server
```bash
# Option 1: Python HTTP server (recommended)
python3 -m http.server 8080

# Option 2: Node.js server (if you have Node.js)
npx http-server -p 8080

# Option 3: PHP server (if you have PHP)
php -S localhost:8080
```

### Step 4: Verify Deployment
Open your browser and navigate to:
- **Checkout App**: http://localhost:8080/checkout.html
- **API Endpoints**: http://localhost:8080/api_endpoints.json

### Step 5: Run Tests
```bash
# In a new terminal (keep web server running)
cd ocean-ai
source venv/bin/activate  # Activate virtual environment

# Generate test cases
python3 test_case_generator.py

# Run Selenium automation
python3 selenium_automation.py

# Run quick demo
python3 qa_demo_lite.py
```

---

## 🏢 Production Server Deployment

### For Ubuntu/Debian Server

#### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv git wget curl

# Install Chrome for headless testing
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install Nginx (for web server)
sudo apt install -y nginx
```

#### Step 2: Deploy Application
```bash
# Create deployment directory
sudo mkdir -p /var/www/ocean-ai
sudo chown $USER:$USER /var/www/ocean-ai

# Clone repository
cd /var/www/ocean-ai
git clone https://github.com/Divyansh-Kumawat/ocean-ai.git .

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install webdriver-manager gunicorn
```

#### Step 3: Configure Nginx
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/ocean-ai << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    root /var/www/ocean-ai;
    index checkout.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/ocean-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 4: Create Systemd Services
```bash
# Create test runner service
sudo tee /etc/systemd/system/ocean-ai-tests.service << 'EOF'
[Unit]
Description=Ocean AI QA Test Runner
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ocean-ai
Environment=PATH=/var/www/ocean-ai/venv/bin
ExecStart=/var/www/ocean-ai/venv/bin/python3 selenium_automation.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ocean-ai-tests
sudo systemctl start ocean-ai-tests
```

---

## 🐳 Docker Deployment

### Step 1: Create Dockerfile
```bash
# Create Dockerfile in project root
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir webdriver-manager

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Create startup script
RUN echo '#!/bin/bash\npython3 -m http.server 8080 &\nexec "$@"' > /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh", "python3", "selenium_automation.py"]
EOF
```

### Step 2: Create Docker Compose
```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  ocean-ai-app:
    build: .
    container_name: ocean-ai-checkout
    ports:
      - "8080:8080"
    volumes:
      - ./test-results:/app/test-results
    environment:
      - DISPLAY=:99
    restart: unless-stopped
    
  ocean-ai-tests:
    build: .
    container_name: ocean-ai-tests
    depends_on:
      - ocean-ai-app
    volumes:
      - ./test-results:/app/test-results
    environment:
      - DISPLAY=:99
      - CHROME_OPTIONS=--headless --no-sandbox --disable-dev-shm-usage
    command: python3 selenium_automation.py
    restart: "no"

volumes:
  test-results:
EOF
```

### Step 3: Build and Run
```bash
# Build Docker image
docker-compose build

# Run services
docker-compose up -d

# Check logs
docker-compose logs -f ocean-ai-app
docker-compose logs -f ocean-ai-tests

# Run one-off test
docker-compose run --rm ocean-ai-tests python3 qa_demo.py
```

---

## 🔄 CI/CD Pipeline Integration

### GitHub Actions Workflow

Create `.github/workflows/qa-tests.yml`:
```yaml
name: QA Testing Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  qa-tests:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install Chrome
      run: |
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt update
        sudo apt install -y google-chrome-stable
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install webdriver-manager pytest-html
        
    - name: Start web server
      run: |
        python -m http.server 8080 &
        sleep 5
        
    - name: Generate test cases
      run: python test_case_generator.py
      
    - name: Run Selenium tests
      run: |
        python selenium_automation.py
        
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: |
          test-results/
          *.html
          *.json
        retention-days: 30
        
    - name: Notify on failure
      if: failure()
      run: |
        echo "QA tests failed! Check the logs for details."
        # Add notification logic (Slack, email, etc.)
```

### Jenkins Pipeline

Create `Jenkinsfile`:
```groovy
pipeline {
    agent any
    
    environment {
        CHROME_BIN = '/usr/bin/google-chrome'
        DISPLAY = ':99'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install webdriver-manager
                '''
            }
        }
        
        stage('Start Application') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -m http.server 8080 &
                    sleep 10
                '''
            }
        }
        
        stage('Generate Test Cases') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 test_case_generator.py
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    export CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage"
                    python3 selenium_automation.py
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '*.json, *.html', fingerprint: true
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: false,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'test_report.html',
                reportName: 'QA Test Report'
            ])
        }
        failure {
            emailext (
                subject: "QA Tests Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "The QA test pipeline has failed. Check console output for details.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

---

## ☁️ Cloud Deployment

### AWS Deployment (EC2 + Load Balancer)

#### Step 1: Launch EC2 Instance
```bash
# Create EC2 instance (Amazon Linux 2)
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-1234567890abcdef0 \
    --subnet-id subnet-12345678 \
    --user-data file://user-data.sh
```

#### Create `user-data.sh`:
```bash
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git docker

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
yum install -y google-chrome-stable_current_x86_64.rpm

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Deploy application
cd /opt
git clone https://github.com/Divyansh-Kumawat/ocean-ai.git
cd ocean-ai
python3 -m pip install -r requirements.txt
python3 -m pip install webdriver-manager

# Start services
python3 -m http.server 8080 &
```

#### Step 2: Setup Load Balancer
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
    --name ocean-ai-alb \
    --subnets subnet-12345678 subnet-87654321 \
    --security-groups sg-1234567890abcdef0
```

### Azure Deployment (Container Instances)

#### Step 1: Create Resource Group
```bash
az group create --name ocean-ai-rg --location eastus
```

#### Step 2: Deploy Container
```bash
az container create \
    --resource-group ocean-ai-rg \
    --name ocean-ai-container \
    --image your-registry/ocean-ai:latest \
    --dns-name-label ocean-ai-app \
    --ports 8080 \
    --environment-variables CHROME_OPTIONS="--headless --no-sandbox"
```

### Google Cloud Platform (Cloud Run)

#### Step 1: Build and Push Image
```bash
# Build and tag image
docker build -t gcr.io/your-project-id/ocean-ai:latest .

# Push to Container Registry
docker push gcr.io/your-project-id/ocean-ai:latest
```

#### Step 2: Deploy to Cloud Run
```bash
gcloud run deploy ocean-ai \
    --image gcr.io/your-project-id/ocean-ai:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 1
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. ChromeDriver Issues
```bash
# Error: chromedriver not found
# Solution: Install webdriver-manager
pip install webdriver-manager

# Use in code:
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
driver = webdriver.Chrome(ChromeDriverManager().install())
```

#### 2. Permission Denied (Linux)
```bash
# Error: Permission denied
# Solution: Fix permissions
sudo chown -R $USER:$USER /var/www/ocean-ai
chmod +x selenium_automation.py
```

#### 3. Port Already in Use
```bash
# Error: Address already in use
# Solution: Kill existing process
sudo lsof -ti:8080 | xargs kill -9
```

#### 4. Chrome in Docker
```bash
# Error: Chrome crashes in Docker
# Solution: Add Chrome options
export CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage --disable-gpu"
```

#### 5. Memory Issues
```bash
# Error: Out of memory
# Solution: Increase container memory or add swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Debug Commands
```bash
# Check if web server is running
curl -I http://localhost:8080/checkout.html

# Check Chrome installation
google-chrome --version

# Check Python dependencies
python3 -c "import selenium; print(selenium.__version__)"

# Test Selenium connection
python3 -c "
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('http://localhost:8080/checkout.html')
print('✅ Selenium working:', driver.title)
driver.quit()
"

# Monitor resource usage
htop  # or top
df -h  # disk space
free -m  # memory usage
```

### Performance Optimization
```bash
# Enable gzip compression (Nginx)
sudo tee -a /etc/nginx/sites-available/ocean-ai << 'EOF'
    gzip on;
    gzip_types text/css application/javascript application/json;
EOF

# Optimize Chrome for headless mode
export CHROME_OPTIONS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage --disable-extensions --disable-plugins"
```

---

## 📊 Monitoring and Logs

### Application Logs
```bash
# View real-time logs
tail -f /var/log/ocean-ai/app.log

# Check systemd service logs
sudo journalctl -u ocean-ai-tests -f

# Docker logs
docker logs -f ocean-ai-checkout
```

### Health Checks
```bash
# Create health check endpoint
curl http://localhost:8080/checkout.html
curl -f http://localhost:8080/api_endpoints.json || echo "API not accessible"
```

### Automated Monitoring Script
```bash
#!/bin/bash
# monitoring.sh
URL="http://localhost:8080/checkout.html"
if curl -f -s $URL > /dev/null; then
    echo "✅ Application is healthy"
    exit 0
else
    echo "❌ Application is down"
    # Restart service
    sudo systemctl restart ocean-ai-tests
    exit 1
fi
```

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Local development
python3 -m http.server 8080
python3 selenium_automation.py

# Docker
docker-compose up -d
docker-compose logs -f

# Production
sudo systemctl status ocean-ai-tests
sudo nginx -t && sudo systemctl reload nginx

# Testing
python3 test_case_generator.py
python3 qa_demo_lite.py
```

### URLs After Deployment
- **Local**: http://localhost:8080/checkout.html
- **Production**: http://your-domain.com/checkout.html
- **Docker**: http://localhost:8080/checkout.html
- **Cloud**: Check cloud provider console for assigned URL

### Support
- **Documentation**: README.md
- **Test Cases**: comprehensive_test_cases.json
- **Configuration**: requirements.txt
- **Issues**: Check GitHub repository issues

---

*This deployment guide covers all major deployment scenarios. Choose the method that best fits your infrastructure and requirements. For additional help, refer to the project documentation or create an issue in the GitHub repository.*