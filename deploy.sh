#!/bin/bash
# Quick deployment script for Render

echo "🚀 Preparing Ocean AI for Render deployment..."

# Add all files
git add .

# Commit with timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "feat: production Docker deployment ready - $TIMESTAMP

- Optimized Dockerfile with minimal dependencies
- Production startup script with fallback
- Streamlit health checks and monitoring
- Clean build with proper caching
- Ready for Render.com deployment"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Deployment ready!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://render.com"
echo "2. Click 'New +' → 'Blueprint'"
echo "3. Select your GitHub repo"
echo "4. Render will auto-deploy using render.yaml"
echo ""
echo "🌐 Your app will be live at:"
echo "https://ocean-ai-qa-framework.onrender.com"
echo ""
echo "🎉 Done! Your AI QA Framework will be live in 5-10 minutes!"