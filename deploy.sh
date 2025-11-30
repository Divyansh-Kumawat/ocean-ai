#!/bin/bash

# 🌊 Ocean AI QA Framework - Render Deployment Script
# Production-ready deployment with lightweight dependencies

echo "🌊 Ocean AI QA Framework - Render Deployment Setup"
echo "=================================================="

# Check if we're in the right directory
if [[ ! -f "streamlit_app.py" ]]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   (should contain streamlit_app.py)"
    exit 1
fi

echo "📋 Deployment Configuration:"
echo "   ✅ Dockerfile (optimized for Render)"
echo "   ✅ render.yaml (Streamlit configuration)"
echo "   ✅ requirements-render.txt (lightweight deps)"
echo "   ✅ production_start.py (smart app selection)"
echo "   ✅ streamlit_lite.py (fallback app)"

echo ""
echo "🔍 File Status Check:"

# Check essential files
files=(
    "Dockerfile"
    "render.yaml"
    "requirements-render.txt"
    "production_start.py"
    "streamlit_app.py"
    "streamlit_lite.py"
)

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (MISSING)"
    fi
done

echo ""
echo "📦 Requirements Analysis:"
echo "   📄 requirements-render.txt (production):"
cat requirements-render.txt | sed 's/^/      /'

echo ""
echo "🚀 Render Deployment Instructions:"
echo "   1. Commit all files to your Git repository:"
echo "      git add ."
echo "      git commit -m 'Production deployment ready'"
echo "      git push origin main"
echo ""
echo "   2. In Render Dashboard:"
echo "      - Create new Web Service"
echo "      - Connect your repository"
echo "      - Choose Docker as build environment"
echo "      - Set branch and auto-deploy"
echo ""
echo "   3. Render will automatically:"
echo "      - Use Dockerfile for build"
echo "      - Use render.yaml for configuration"
echo "      - Start with production_start.py"
echo "      - Auto-select lightweight or full app"

echo ""
echo "🔧 Environment Variables (set in Render):"
echo "   PORT=8080 (auto-set by Render)"
echo "   PYTHONUNBUFFERED=1 (recommended)"

echo ""
echo "🎯 Deployment Strategy:"
echo "   📱 Primary: streamlit_lite.py (lightweight, no ML)"
echo "   🔄 Fallback: streamlit_app.py (if dependencies available)"
echo "   🌐 Last resort: Simple HTTP server"

echo ""
echo "✅ Your app is ready for Render deployment!"
echo "   🌐 Health check: /_stcore/health"
echo "   🏠 Main app: / (root)"
echo "   ⏱️ Startup timeout: 60 seconds"

echo ""
echo "🆘 If deployment fails:"
echo "   1. Check Render logs for specific errors"
echo "   2. App will auto-fallback to lightweight version"
echo "   3. Update requirements-render.txt if needed"
echo "   4. Contact support with specific error messages"

echo ""
echo "Happy deploying! 🚀"
echo ""
echo "🌐 Your app will be live at:"
echo "https://ocean-ai-qa-framework.onrender.com"
echo ""
echo "🎉 Done! Your AI QA Framework will be live in 5-10 minutes!"