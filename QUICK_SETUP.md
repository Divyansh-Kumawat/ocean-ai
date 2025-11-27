# Ocean AI Quick Setup Guide 🌊

## 📋 Prerequisites
- Python 3.8+ installed
- Internet connection for downloading packages

## 🚀 Quick Start

### 1. Set up your Gemini API Key (Recommended for AI features)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a free API key
3. Update the `.env` file in this directory:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

**Note:** The .env file is already created with a placeholder. You just need to replace `your_gemini_api_key_here` with your actual API key.

### 2. Launch the Application

**Option A: Using the launcher script (Recommended)**
```bash
python launch_streamlit.py
```

**Option B: Direct Streamlit launch**
```bash
python -m streamlit run streamlit_app.py
```

### 3. Access the Application
- Open your browser to: http://localhost:8501
- The application will automatically open in your default browser

## ✨ Features Available

### Without API Key (Basic Mode)
- Knowledge base document upload and processing
- Rule-based test case generation
- Selenium script generation
- Vector database search

### With Gemini API Key (AI-Powered Mode)
- AI-powered test case generation
- Intelligent context analysis
- Advanced query understanding
- Enhanced test scenario creation

## 🔧 Troubleshooting

### Dependencies Issues
If you encounter package installation errors:
```bash
pip install -r requirements-streamlit-fixed.txt
```

### Port Already in Use
If port 8501 is busy, modify the `.env` file:
```
APP_PORT=8502
```

### API Key Issues
- Ensure your API key is valid and active
- Check that there are no extra spaces in the .env file
- Restart the application after updating the API key

## 📂 Project Structure
```
ocean-ai/
├── .env                    # Environment configuration
├── streamlit_app.py        # Main Streamlit application
├── launch_streamlit.py     # Launcher script
├── requirements-streamlit-fixed.txt  # Dependencies
├── product_specs.md        # Sample documentation
├── checkout.html          # Sample HTML for testing
└── README.md              # This file
```

## 🎯 Next Steps
1. Upload your project documentation using the app interface
2. Generate test cases using natural language queries
3. Download generated Selenium scripts
4. Integrate with your CI/CD pipeline

## 🆘 Need Help?
- Check that all requirements are installed
- Ensure your Python version is 3.8+
- Verify your internet connection for package downloads
- Make sure the .env file is properly formatted

Happy Testing! 🧪✨