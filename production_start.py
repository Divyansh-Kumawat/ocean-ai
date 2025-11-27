#!/usr/bin/env python3
"""
Production startup script for Ocean AI QA Framework on Render
Serves the Streamlit app with health checks and proper configuration
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

# Global variables
PORT = int(os.environ.get('PORT', 10000))
running = True

def signal_handler(sig, frame):
    """Handle graceful shutdown"""
    global running
    print('🛑 Graceful shutdown initiated...')
    running = False
    sys.exit(0)

def create_streamlit_config():
    """Create Streamlit configuration for production"""
    config_dir = Path.home() / '.streamlit'
    config_dir.mkdir(exist_ok=True)
    
    config_content = f"""
[server]
port = {PORT}
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
base = "light"
"""
    
    config_file = config_dir / 'config.toml'
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Streamlit config created at {config_file}")

def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = ['streamlit', 'pandas', 'requests']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} missing")
    
    if missing:
        print(f"⚠️ Installing missing packages: {missing}")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--no-cache-dir'
            ] + missing, check=True)
            print("✅ Missing packages installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")

def start_streamlit():
    """Start the Streamlit application"""
    try:
        print(f"🌊 Starting Ocean AI QA Framework on port {PORT}")
        print(f"🔗 App will be available at: https://your-app.onrender.com")
        
        # Create config
        create_streamlit_config()
        
        # Check dependencies
        check_dependencies()
        
        # Start Streamlit
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.port', str(PORT),
            '--server.address', '0.0.0.0',
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--server.enableCORS', 'false',
            '--server.enableXsrfProtection', 'false'
        ]
        
        print(f"🚀 Running command: {' '.join(cmd)}")
        
        # Run Streamlit
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Monitor output
        while running and process.poll() is None:
            line = process.stdout.readline()
            if line:
                print(line.strip())
        
        return process.returncode
        
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return 1

def fallback_server():
    """Fallback HTTP server if Streamlit fails"""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import json
    
    class FallbackHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                health_data = {
                    "status": "healthy",
                    "service": "Ocean AI QA Framework (Fallback)",
                    "message": "Streamlit unavailable, serving static content",
                    "timestamp": time.time()
                }
                self.wfile.write(json.dumps(health_data).encode())
            elif self.path == '/' or self.path == '':
                self.path = '/checkout.html'
                super().do_GET()
            else:
                super().do_GET()
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), FallbackHandler)
        print(f"🔄 Fallback server running on port {PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Fallback server error: {e}")

if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Ocean AI QA Framework - Production Startup")
    print("=" * 60)
    print(f"📍 Port: {PORT}")
    print(f"🔧 Chrome Options: {os.environ.get('CHROME_OPTIONS', 'default')}")
    print("=" * 60)
    
    # Check if streamlit_app.py exists
    if not Path('streamlit_app.py').exists():
        print("❌ streamlit_app.py not found, starting fallback server")
        fallback_server()
    else:
        # Try to start Streamlit
        return_code = start_streamlit()
        
        if return_code != 0:
            print("⚠️ Streamlit failed, starting fallback server")
            fallback_server()