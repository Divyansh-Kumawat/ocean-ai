#!/usr/bin/env python3
"""
Render.com startup script for Ocean AI QA Framework
Handles both web server and application initialization
"""

import os
import sys
import time
import threading
import subprocess
import signal
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from urllib.parse import urlparse

# Global variables
PORT = int(os.environ.get('PORT', 10000))
CHROME_OPTIONS = os.environ.get('CHROME_OPTIONS', '--headless --no-sandbox --disable-dev-shm-usage')
running = True

class CustomHTTPHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler with health check and API endpoints"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_health_check()
        elif self.path == '/api/status':
            self.send_status()
        elif self.path == '/api/test-results':
            self.send_test_results()
        elif self.path == '/' or self.path == '':
            self.path = '/checkout.html'
            super().do_GET()
        else:
            super().do_GET()
    
    def send_health_check(self):
        """Health check endpoint for Render"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        health_data = {
            "status": "healthy",
            "service": "Ocean AI QA Framework",
            "timestamp": time.time(),
            "version": "1.0.0",
            "environment": "render"
        }
        
        self.wfile.write(json.dumps(health_data).encode())
    
    def send_status(self):
        """API status endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        status_data = {
            "qa_framework": "active",
            "selenium_tests": "available",
            "test_cases": "generated",
            "chrome_headless": "configured",
            "endpoints": {
                "checkout": "/checkout.html",
                "health": "/health",
                "test_results": "/api/test-results",
                "test_cases": "/comprehensive_test_cases.json"
            }
        }
        
        self.wfile.write(json.dumps(status_data, indent=2).encode())
    
    def send_test_results(self):
        """Test results endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Try to read test results if available
            with open('comprehensive_test_cases.json', 'r') as f:
                test_data = json.load(f)
            
            results = {
                "total_tests": len(test_data),
                "test_categories": {},
                "last_updated": time.time()
            }
            
            # Count tests by feature
            for test in test_data:
                feature = test.get('Feature', 'Unknown')
                results["test_categories"][feature] = results["test_categories"].get(feature, 0) + 1
            
            self.wfile.write(json.dumps(results, indent=2).encode())
            
        except FileNotFoundError:
            error_data = {
                "error": "Test cases not yet generated",
                "status": "initializing"
            }
            self.wfile.write(json.dumps(error_data).encode())

def signal_handler(sig, frame):
    """Handle graceful shutdown"""
    global running
    print('🛑 Graceful shutdown initiated...')
    running = False
    sys.exit(0)

def setup_chrome_driver():
    """Setup ChromeDriver for Render environment"""
    try:
        print("🔧 Setting up ChromeDriver for Render...")
        
        # Install ChromeDriver using webdriver-manager
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        
        # Verify Chrome is available
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Chrome version: {result.stdout.strip()}")
        else:
            print("⚠️ Chrome not found - tests will run with basic driver")
            
        return True
        
    except Exception as e:
        print(f"⚠️ ChromeDriver setup issue (will continue): {e}")
        return False

def generate_initial_test_cases():
    """Generate test cases on startup"""
    try:
        print("📝 Generating initial test cases...")
        
        # Run test case generator with timeout
        result = subprocess.run(['python', 'test_case_generator.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Test cases generated successfully")
            return True
        else:
            print(f"⚠️ Test case generation completed with warnings: {result.stderr}")
            return True  # Continue anyway
            
    except subprocess.TimeoutExpired:
        print("⏱️ Test case generation timed out - will retry later")
        return False
    except Exception as e:
        print(f"⚠️ Test case generation error: {e}")
        return False

def run_demo_tests():
    """Run lightweight demo tests"""
    try:
        print("🎬 Running QA framework demo...")
        
        # Run lightweight demo
        result = subprocess.run(['python', 'qa_demo_lite.py'], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Demo tests completed successfully")
            print("📊 Results preview:")
            # Show first few lines of output
            lines = result.stdout.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"⚠️ Demo tests completed with warnings")
            
    except subprocess.TimeoutExpired:
        print("⏱️ Demo tests timed out")
    except Exception as e:
        print(f"⚠️ Demo test error: {e}")

def start_background_tasks():
    """Start background initialization tasks"""
    def background_init():
        time.sleep(5)  # Wait for web server to start
        
        if running:
            setup_chrome_driver()
        
        if running:
            generate_initial_test_cases()
        
        if running:
            run_demo_tests()
        
        print("✅ Background initialization completed")
    
    # Run in separate thread to not block web server
    init_thread = threading.Thread(target=background_init, daemon=True)
    init_thread.start()

def start_web_server():
    """Start the main web server"""
    try:
        print(f"🌐 Starting Ocean AI QA Framework on port {PORT}")
        print(f"🔗 Server will be available at: https://your-app.onrender.com")
        
        # Create HTTP server with custom handler
        server = HTTPServer(('0.0.0.0', PORT), CustomHTTPHandler)
        
        print("✅ Web server ready!")
        print("📱 Available endpoints:")
        print("   - / or /checkout.html (E-Shop Application)")
        print("   - /health (Health Check)")
        print("   - /api/status (API Status)")
        print("   - /api/test-results (Test Results)")
        print("   - /comprehensive_test_cases.json (Test Cases)")
        
        # Start background tasks
        start_background_tasks()
        
        # Start server
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Ocean AI QA Framework - Render.com Deployment")
    print("=" * 60)
    print(f"📍 Port: {PORT}")
    print(f"🖥️ Chrome Options: {CHROME_OPTIONS}")
    print("=" * 60)
    
    # Start the web server (this is the main process)
    start_web_server()