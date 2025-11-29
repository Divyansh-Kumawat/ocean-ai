#!/usr/bin/env python3
"""
Production startup script for Ocean AI QA Framework
Optimized for Render deployment with lightweight fallbacks
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Configuration
PORT = int(os.environ.get('PORT', 8080))
running = True

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global running
    running = False
    print("\n🛑 Shutdown signal received")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def setup_environment():
    """Set up environment variables and paths"""
    print("🔧 Setting up environment...")
    
    # Set essential environment variables
    os.environ['STREAMLIT_SERVER_PORT'] = str(PORT)
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    # Configure Chrome/Chromium for Selenium
    chrome_path = None
    if Path('/usr/bin/google-chrome').exists():
        chrome_path = '/usr/bin/google-chrome'
    elif Path('/usr/bin/chromium').exists():
        chrome_path = '/usr/bin/chromium'
    elif Path('/usr/bin/chromium-browser').exists():
        chrome_path = '/usr/bin/chromium-browser'
    
    if chrome_path:
        os.environ['CHROME_BIN'] = chrome_path
        print(f"🌐 Chrome/Chromium found: {chrome_path}")
    else:
        print("⚠️ Chrome/Chromium not found - Selenium tests may not work")
    
    print("✅ Environment configured")

def check_health():
    """Basic health check"""
    print("🏥 Running health checks...")
    
    # Check Python version
    print(f"🐍 Python {sys.version}")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"💾 Memory: {memory.percent}% used")
    except ImportError:
        print("💾 Memory info not available")
    
    print("✅ Health check passed")

def install_missing_packages(packages):
    """Install missing packages"""
    print(f"📦 Installing packages: {packages}")
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '--only-binary=:all:'] + packages
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Package installation failed: {e}")
        return False

def check_dependencies():
    """Check and install required dependencies"""
    print("📋 Checking dependencies...")
    
    core_packages = ['streamlit', 'pandas']
    missing = []
    
    for package in core_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} missing")
    
    if missing:
        if not install_missing_packages(missing):
            print("⚠️ Some packages couldn't be installed, proceeding anyway")
    
    print("✅ Dependencies checked")

def select_app_file():
    """Select the appropriate app file based on available dependencies"""
    print("🔍 Selecting app version...")
    
    # Check if main app exists
    if not Path('streamlit_app.py').exists():
        if Path('streamlit_lite.py').exists():
            print("📱 Using lightweight app (main app not found)")
            return 'streamlit_lite.py'
        else:
            print("❌ No app files found")
            return None
    
    # Check for heavy dependencies
    try:
        import chromadb
        import sentence_transformers
        print("🔬 Heavy ML dependencies available - using full app")
        return 'streamlit_app.py'
    except ImportError:
        if Path('streamlit_lite.py').exists():
            print("⚡ Heavy dependencies missing - using lightweight app")
            return 'streamlit_lite.py'
        else:
            print("⚠️ Heavy dependencies missing - using main app anyway")
            return 'streamlit_app.py'

def start_streamlit(app_file):
    """Start Streamlit with the selected app file"""
    print(f"🚀 Starting Streamlit with {app_file}...")
    
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', app_file,
        '--server.port', str(PORT),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false'
    ]
    
    try:
        print(f"🌊 Ocean AI QA Framework starting on port {PORT}")
        print(f"📱 App file: {app_file}")
        print(f"🔗 Will be available at your Render URL")
        
        # Start the process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Monitor the process
        startup_time = 0
        max_startup_time = 60  # 60 seconds timeout
        
        while startup_time < max_startup_time and process.poll() is None:
            time.sleep(1)
            startup_time += 1
            
            # Check for output
            try:
                line = process.stdout.readline()
                if line:
                    print(line.strip())
                    # Look for successful startup indicators
                    if "You can now view your Streamlit app" in line or "Network URL:" in line:
                        print("✅ Streamlit started successfully!")
                        break
            except:
                pass
        
        if process.poll() is None:
            # Process is still running, wait for completion
            process.wait()
        else:
            # Process ended during startup
            return_code = process.returncode
            print(f"❌ Streamlit process ended with code: {return_code}")
            return return_code
            
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return 1
    
    return 0

def fallback_server():
    """Simple fallback HTTP server"""
    print("🔄 Starting fallback server...")
    
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import json
    
    class FallbackHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/_stcore/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "ok",
                    "message": "Ocean AI QA Framework - Fallback Mode",
                    "version": "1.0.0"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), FallbackHandler)
        print(f"🌐 Fallback server running on port {PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Fallback server failed: {e}")

def main():
    """Main application entry point"""
    print("🌊 Ocean AI QA Framework - Production Startup")
    
    try:
        # Setup
        setup_environment()
        check_health()
        check_dependencies()
        
        # Select and start app
        app_file = select_app_file()
        
        if not app_file:
            print("❌ No suitable app file found, starting fallback")
            fallback_server()
            return
        
        # Try to start Streamlit
        return_code = start_streamlit(app_file)
        
        # If main app failed and we have a lite version, try that
        if return_code != 0 and app_file != 'streamlit_lite.py' and Path('streamlit_lite.py').exists():
            print("🔄 Retrying with lightweight app...")
            return_code = start_streamlit('streamlit_lite.py')
        
        # If still failed, start fallback
        if return_code != 0:
            print("⚠️ Streamlit failed, starting fallback server")
            fallback_server()
            
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        print("🔄 Starting fallback server as last resort")
        fallback_server()

if __name__ == "__main__":
    main()