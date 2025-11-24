# 🚀 Render.com Deployment Guide

## Step-by-Step Deployment Instructions

### Prerequisites
- GitHub account
- Render.com account (free tier available)
- Your Ocean AI repository pushed to GitHub

---

## 📋 **Step 1: Prepare Your Repository**

Ensure these files are in your repository (already created):
- ✅ `render.yaml` - Render configuration
- ✅ `render_start.py` - Main startup script  
- ✅ `test_runner_service.py` - Background test runner
- ✅ `requirements.txt` - Updated with Render dependencies

### Verify files are ready:
```bash
ls -la | grep -E "(render|requirements)"
# Should show: render.yaml, render_start.py, test_runner_service.py, requirements.txt
```

---

## 🌐 **Step 2: Deploy to Render**

### Option A: Deploy via GitHub (Recommended)

1. **Push to GitHub** (if not already done):
```bash
git add .
git commit -m "feat: add Render deployment configuration"
git push origin main
```

2. **Login to Render**: Go to [render.com](https://render.com)

3. **Connect Repository**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub account
   - Select your `ocean-ai` repository
   - Render will automatically detect the `render.yaml` file

4. **Configure Environment**:
   - **Service Name**: `ocean-ai-qa-framework`
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - Click "Apply"

### Option B: Deploy via Render Dashboard

1. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect GitHub → Select `ocean-ai` repository
   - Configure:
     ```
     Name: ocean-ai-qa-framework
     Runtime: Python 3
     Build Command: pip install -r requirements.txt && pip install webdriver-manager gunicorn
     Start Command: python render_start.py
     ```

2. **Set Environment Variables**:
   ```
   PORT=10000
   CHROME_OPTIONS=--headless --no-sandbox --disable-dev-shm-usage --disable-gpu --single-process
   PYTHONPATH=.
   ```

---

## ⏱️ **Step 3: Monitor Deployment**

### Watch the Build Process:
1. **Build Logs**: Click on your service → "Logs" tab
2. **Expected Build Steps**:
   ```
   ✅ Installing Python dependencies...
   ✅ Installing Chrome and ChromeDriver...
   ✅ Setting up Selenium environment...
   ✅ Build completed successfully
   ```

### Deployment Timeline:
- **Build Phase**: ~3-5 minutes
- **Chrome Installation**: ~2-3 minutes  
- **First Boot**: ~1-2 minutes
- **Total**: ~6-10 minutes

---

## 🔍 **Step 4: Verify Deployment**

### Your app will be available at:
```
https://ocean-ai-qa-framework.onrender.com
```

### Test these endpoints:

1. **Main Application**:
   ```bash
   curl https://ocean-ai-qa-framework.onrender.com/
   # Should redirect to checkout.html
   ```

2. **Health Check**:
   ```bash
   curl https://ocean-ai-qa-framework.onrender.com/health
   # Should return JSON with status: "healthy"
   ```

3. **API Status**:
   ```bash
   curl https://ocean-ai-qa-framework.onrender.com/api/status
   # Should return QA framework status
   ```

4. **Test Cases**:
   ```bash
   curl https://ocean-ai-qa-framework.onrender.com/comprehensive_test_cases.json
   # Should return your generated test cases
   ```

---

## 🎯 **Step 5: Test the QA Framework**

### Access Your Application:
1. **Open Browser**: Navigate to your Render URL
2. **Test E-Shop**: Use the checkout application
   - Add items to cart
   - Apply discount codes (SAVE15, WELCOME10)
   - Test form validation
   - Complete checkout process

### View QA Framework Features:
1. **Test Results**: Visit `/api/test-results`
2. **Generated Tests**: Download `/comprehensive_test_cases.json`
3. **System Status**: Check `/api/status`

---

## 🛠️ **Step 6: Configure Custom Domain (Optional)**

### Add Custom Domain:
1. **Render Dashboard**: Go to your service settings
2. **Custom Domains**: Click "Add Custom Domain"
3. **Enter Domain**: `your-domain.com`
4. **DNS Setup**: Add CNAME record:
   ```
   CNAME: www.your-domain.com → ocean-ai-qa-framework.onrender.com
   ```

---

## 📊 **Step 7: Monitor Performance**

### Render Dashboard Features:
- **Metrics**: CPU, Memory, Response times
- **Logs**: Real-time application logs
- **Deployments**: History and rollback options
- **Health**: Automatic health monitoring

### Key Metrics to Watch:
- **Response Time**: Should be < 2 seconds
- **Memory Usage**: Typically 200-400MB
- **CPU Usage**: Low when idle, spikes during tests

---

## 🔧 **Troubleshooting Common Issues**

### Issue 1: Build Fails
```bash
# Check build logs for specific error
# Common fix: Update requirements.txt versions
```

### Issue 2: Chrome/ChromeDriver Issues
```bash
# Error: Chrome binary not found
# Solution: Chrome is automatically installed by Render
# Wait for complete deployment (~10 minutes)
```

### Issue 3: Memory Issues  
```bash
# Error: Application killed (OOM)
# Solution: Upgrade to Render paid plan for more memory
# Or optimize Chrome options in render.yaml
```

### Issue 4: Slow Response
```bash
# Render free tier sleeps after 15 minutes of inactivity
# First request after sleep takes ~30 seconds to wake up
# Solution: Upgrade to paid plan for always-on service
```

---

## 🔄 **Step 8: Continuous Deployment**

### Auto-Deploy Setup:
1. **GitHub Integration**: Already configured
2. **Auto-Deploy**: Enabled by default
3. **Branch Protection**: Set to `main` branch

### Deployment Workflow:
```bash
# Make changes locally
git add .
git commit -m "feat: your changes"
git push origin main

# Render automatically:
# 1. Detects changes
# 2. Rebuilds application  
# 3. Deploys new version
# 4. Runs health checks
```

---

## 💰 **Render Pricing & Limits**

### Free Tier Includes:
- ✅ 750 build hours/month
- ✅ Always-on web services (with sleep after 15min idle)
- ✅ 100GB bandwidth
- ✅ Custom domains
- ✅ SSL certificates

### Free Tier Limitations:
- ⚠️ Apps sleep after 15 minutes idle
- ⚠️ 512MB RAM limit
- ⚠️ Shared CPU

### Upgrade Benefits ($7/month):
- 🚀 Always-on services (no sleep)
- 🚀 More memory and CPU
- 🚀 Faster builds
- 🚀 Priority support

---

## 📁 **Final File Structure**

Your deployed repository should contain:
```
ocean-ai/
├── render.yaml              # Render configuration  
├── render_start.py          # Main startup script
├── test_runner_service.py   # Background test runner
├── requirements.txt         # Updated dependencies
├── checkout.html            # E-Shop application
├── test_case_generator.py   # QA framework
├── selenium_automation.py   # Test automation
├── comprehensive_test_cases.json # Test cases
└── ... (other files)
```

---

## ✅ **Success Checklist**

Before considering deployment complete:

- [ ] Repository pushed to GitHub with all Render files
- [ ] Render service created and deployed successfully  
- [ ] Health check endpoint returns 200 status
- [ ] Main checkout application loads correctly
- [ ] API endpoints respond with valid JSON
- [ ] Test cases are generated and accessible
- [ ] Chrome/Selenium is working (check logs)
- [ ] Custom domain configured (if desired)
- [ ] Monitoring and alerts set up

---

## 🎉 **You're Live!**

Your Ocean AI QA Framework is now deployed on Render! 

**Share your application**:
- 🔗 Main App: `https://ocean-ai-qa-framework.onrender.com`
- 🔗 Health Check: `https://ocean-ai-qa-framework.onrender.com/health`
- 🔗 API Status: `https://ocean-ai-qa-framework.onrender.com/api/status`

**Next Steps**:
- Share the URL with your team
- Set up monitoring alerts
- Consider upgrading for production workloads
- Add more test cases and automation

---

## 📞 **Support & Resources**

- **Render Docs**: [docs.render.com](https://docs.render.com)
- **Render Community**: [community.render.com](https://community.render.com)
- **Your Project**: Check GitHub repository for updates
- **Issues**: Report issues in your GitHub repository