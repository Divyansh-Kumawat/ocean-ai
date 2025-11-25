#!/usr/bin/env python3
"""
Quick setup and launch script for Ocean AI Streamlit QA Agent
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    try:
        print("📦 Installing Streamlit dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements-streamlit.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit as st
        print(f"✅ Streamlit version: {st.__version__}")
        return True
    except ImportError:
        print("❌ Streamlit not installed")
        return False

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking environment configuration...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env file not found!")
        print("📝 Please create .env file and add your Gemini API key")
        print("Get your free API key from: https://aistudio.google.com/app/apikey")
        return True
    
    # Check if Gemini API key is configured
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("⚠️ Gemini API key not configured in .env file")
            print("You can still use the app with basic features")
            print("Get your free API key from: https://aistudio.google.com/app/apikey")
        else:
            print("✅ Gemini API key found and configured")
    except ImportError:
        print("📦 python-dotenv not found in dependencies")
    
    return True

def launch_streamlit():
    """Launch the Streamlit application"""
    try:
        print("🚀 Launching Ocean AI QA Agent...")
        print("🌐 Opening in browser: http://localhost:8501")
        print("💡 Use Ctrl+C to stop the application")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped")
    except Exception as e:
        print(f"❌ Failed to launch Streamlit: {e}")

def main():
    """Main function"""
    print("🌊 Ocean AI - Autonomous QA Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check if requirements file exists
    if not Path("requirements-streamlit.txt").exists():
        print("❌ requirements-streamlit.txt not found")
        return
    
    # Check if Streamlit app exists
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found")
        return
    
    # Install dependencies if needed
    if not check_streamlit():
        if not install_dependencies():
            return
        
        # Verify installation
        if not check_streamlit():
            return
    
    # Check environment configuration
    check_environment()
    
    # Launch application
    launch_streamlit()

if __name__ == "__main__":
    main()