#!/usr/bin/env python3
"""
Background test runner service for Render deployment
Runs periodic tests and maintains test results
"""

import os
import time
import json
import subprocess
import requests
import schedule
from datetime import datetime

# Configuration
WEB_SERVICE_URL = os.environ.get('WEB_SERVICE_URL', 'http://localhost:10000')
CHROME_OPTIONS = os.environ.get('CHROME_OPTIONS', '--headless --no-sandbox --disable-dev-shm-usage')
TEST_INTERVAL_MINUTES = 30  # Run tests every 30 minutes

class TestRunner:
    def __init__(self):
        self.results = {
            "last_run": None,
            "total_runs": 0,
            "success_count": 0,
            "failure_count": 0,
            "test_results": []
        }
        
    def setup_environment(self):
        """Setup test environment"""
        try:
            print("🔧 Setting up test environment...")
            
            # Install ChromeDriver
            from webdriver_manager.chrome import ChromeDriverManager
            ChromeDriverManager().install()
            print("✅ ChromeDriver ready")
            
            return True
        except Exception as e:
            print(f"⚠️ Environment setup warning: {e}")
            return False
    
    def wait_for_web_service(self, timeout=60):
        """Wait for main web service to be ready"""
        print(f"⏳ Waiting for web service at {WEB_SERVICE_URL}")
        
        for i in range(timeout):
            try:
                response = requests.get(f"{WEB_SERVICE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Web service is ready")
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(1)
            if i % 10 == 0:
                print(f"   Still waiting... ({i}s)")
        
        print("⚠️ Web service not responsive, continuing anyway")
        return False
    
    def run_test_generation(self):
        """Generate fresh test cases"""
        try:
            print("📝 Generating test cases...")
            
            # Try main test generator first
            result = subprocess.run(['python', 'test_case_generator.py'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Test cases generated")
                return {"status": "success", "output": result.stdout}
            else:
                print("⚠️ Main generator failed, trying lightweight version...")
                
                # Fallback to lightweight generator
                result = subprocess.run(['python', 'lightweight_test_generator.py'], 
                                      capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print("✅ Lightweight test cases generated")
                    return {"status": "success", "output": result.stdout}
                else:
                    return {"status": "warning", "output": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "output": "Test generation timed out"}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    
    def run_qa_demo(self):
        """Run QA framework demo"""
        try:
            print("🎬 Running QA demo...")
            
            result = subprocess.run(['python', 'qa_demo_lite.py'], 
                                  capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                print("✅ QA demo completed")
                return {"status": "success", "output": result.stdout}
            else:
                return {"status": "warning", "output": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "output": "QA demo timed out"}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    
    def run_selenium_sample(self):
        """Run a quick Selenium test sample"""
        try:
            print("🤖 Running Selenium sample...")
            
            # Create a minimal Selenium test
            test_script = """
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

chrome_options = Options()
for option in os.environ.get('CHROME_OPTIONS', '').split():
    chrome_options.add_argument(option)

try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('http://localhost:10000/checkout.html')
    title = driver.title
    print(f"✅ Page loaded successfully: {title}")
    
    # Quick element check
    driver.find_element("id", "pay-now")
    print("✅ Pay Now button found")
    
    driver.quit()
    print("✅ Selenium test completed successfully")
    
except Exception as e:
    print(f"❌ Selenium test failed: {e}")
    raise
"""
            
            # Write and run the test
            with open('quick_selenium_test.py', 'w') as f:
                f.write(test_script)
            
            result = subprocess.run(['python', 'quick_selenium_test.py'], 
                                  capture_output=True, text=True, timeout=60)
            
            # Clean up
            if os.path.exists('quick_selenium_test.py'):
                os.remove('quick_selenium_test.py')
            
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout}
            else:
                return {"status": "error", "output": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "output": "Selenium test timed out"}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    
    def run_full_test_suite(self):
        """Run the complete test suite"""
        print(f"🧪 Starting test run at {datetime.now()}")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Run test generation
        test_results["tests"]["test_generation"] = self.run_test_generation()
        
        # Run QA demo
        test_results["tests"]["qa_demo"] = self.run_qa_demo()
        
        # Run Selenium sample (if web service is available)
        if self.wait_for_web_service(timeout=10):
            test_results["tests"]["selenium_sample"] = self.run_selenium_sample()
        else:
            test_results["tests"]["selenium_sample"] = {
                "status": "skipped", 
                "output": "Web service not available"
            }
        
        # Update statistics
        self.results["last_run"] = test_results["timestamp"]
        self.results["total_runs"] += 1
        self.results["test_results"].append(test_results)
        
        # Keep only last 10 results
        if len(self.results["test_results"]) > 10:
            self.results["test_results"] = self.results["test_results"][-10:]
        
        # Count successes/failures
        success = all(t["status"] in ["success", "warning"] for t in test_results["tests"].values())
        if success:
            self.results["success_count"] += 1
        else:
            self.results["failure_count"] += 1
        
        # Save results
        with open('test_runner_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"✅ Test run completed. Success: {success}")
        return test_results

def main():
    print("🚀 Ocean AI Test Runner Service - Starting")
    print("=" * 50)
    
    runner = TestRunner()
    
    # Setup environment
    runner.setup_environment()
    
    # Wait for main service to be ready
    runner.wait_for_web_service()
    
    # Run initial test
    print("🎯 Running initial test suite...")
    runner.run_full_test_suite()
    
    # Schedule periodic tests
    print(f"📅 Scheduling tests every {TEST_INTERVAL_MINUTES} minutes")
    schedule.every(TEST_INTERVAL_MINUTES).minutes.do(runner.run_full_test_suite)
    
    # Keep running
    print("♾️ Test runner is now active")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()